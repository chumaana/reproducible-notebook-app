from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import models
from django.utils import timezone
from datetime import datetime
import re
import time

from .models import Notebook, NotebookBlock, NotebookExecution, ReproducibilityAnalysis
from .serializers import (
    NotebookListSerializer,
    NotebookDetailSerializer,
    NotebookBlockSerializer,
    NotebookExecutionSerializer,
    ReproducibilityAnalysisSerializer,
)


class NotebookViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # For development

    def get_queryset(self):
        # For now, return all notebooks (later filter by user)
        return Notebook.objects.all().prefetch_related("blocks")

    def get_serializer_class(self):
        if self.action == "list":
            return NotebookListSerializer
        return NotebookDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def add_block(self, request, pk=None):
        """Add a new block to the notebook"""
        notebook = self.get_object()
        block_type = request.data.get("block_type", "code")

        # Get the highest order number and add 1
        max_order = (
            NotebookBlock.objects.filter(notebook=notebook).aggregate(
                models.Max("order")
            )["order__max"]
            or 0
        )

        block = NotebookBlock.objects.create(
            notebook=notebook, block_type=block_type, content="", order=max_order + 1
        )

        serializer = NotebookBlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def execute_block(self, request, pk=None):
        """Execute a single code block"""
        notebook = self.get_object()
        block_id = request.data.get("block_id")

        try:
            block = NotebookBlock.objects.get(id=block_id, notebook=notebook)

            if block.block_type != "code":
                return Response(
                    {"error": "Cannot execute markdown block"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update status
            block.execution_status = "running"
            block.save()

            # Mock R execution (replace with actual R4R integration later)
            start_time = time.time()

            # Simulate execution delay
            time.sleep(0.5)

            # Mock output based on content
            if "library" in block.content.lower():
                block.output = (
                    f"# Loading required packages\n# Package loaded successfully"
                )
            elif "plot" in block.content.lower() or "ggplot" in block.content.lower():
                block.output = f"# Creating plot...\n# Plot generated successfully\n# Use print() to display"
            elif "data" in block.content.lower():
                block.output = f"# Processing data...\n# [1] Data frame created: 10 rows, 3 columns"
            else:
                block.output = f"# Code executed successfully\n# Output:\n[1] TRUE"

            execution_time = time.time() - start_time

            block.execution_status = "completed"
            block.execution_time = execution_time
            block.error_output = ""
            block.save()

            serializer = NotebookBlockSerializer(block)
            return Response(serializer.data)

        except NotebookBlock.DoesNotExist:
            return Response(
                {"error": "Block not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            if "block" in locals():
                block.execution_status = "failed"
                block.error_output = str(e)
                block.save()

            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def execute_all(self, request, pk=None):
        """Execute all code blocks in the notebook"""
        notebook = self.get_object()

        # Create execution record
        execution = NotebookExecution.objects.create(
            notebook=notebook,
            status="running",
            total_blocks=notebook.blocks.filter(block_type="code").count(),
        )

        completed = 0
        failed = 0

        for block in notebook.blocks.filter(block_type="code").order_by("order"):
            try:
                # Execute block (mock)
                block.execution_status = "running"
                block.save()

                time.sleep(0.3)  # Simulate execution

                block.output = f"# Executed in batch mode\n[1] TRUE"
                block.execution_status = "completed"
                block.save()

                completed += 1
            except Exception as e:
                block.execution_status = "failed"
                block.error_output = str(e)
                block.save()
                failed += 1

        # Update execution record
        execution.status = "completed" if failed == 0 else "failed"
        execution.completed_at = timezone.now()
        execution.completed_blocks = completed
        execution.failed_blocks = failed
        execution.save()

        serializer = NotebookExecutionSerializer(execution)
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post"])
    def analyze_reproducibility(self, request, pk=None):
        """Analyze notebook for reproducibility issues"""
        notebook = self.get_object()

        # Create or get existing analysis
        analysis, created = ReproducibilityAnalysis.objects.get_or_create(
            notebook=notebook,
            defaults={
                "has_random_seed": False,
                "has_hardcoded_paths": False,
                "has_external_deps": False,
                "has_time_deps": False,
                "has_interactive_input": False,
            },
        )

        # Analyze code blocks
        all_code = "\n".join(
            [block.content for block in notebook.blocks.filter(block_type="code")]
        )

        # Check for random seed
        analysis.has_random_seed = bool(
            re.search(r"set\.seed\(", all_code, re.IGNORECASE)
        )

        # Check for hardcoded paths
        path_patterns = [r'["\'][A-Za-z]:\\', r'["\']\/home\/', r'["\']\/Users\/']
        analysis.has_hardcoded_paths = any(
            re.search(pattern, all_code) for pattern in path_patterns
        )

        # Check for external dependencies
        external_patterns = [r"http://", r"https://", r"ftp://", r"download\.file"]
        analysis.has_external_deps = any(
            re.search(pattern, all_code, re.IGNORECASE) for pattern in external_patterns
        )

        # Check for time dependencies
        time_patterns = [r"Sys\.time\(", r"Sys\.Date\(", r"now\("]
        analysis.has_time_deps = any(
            re.search(pattern, all_code, re.IGNORECASE) for pattern in time_patterns
        )

        # Check for interactive input
        analysis.has_interactive_input = bool(
            re.search(r"readline\(|scan\(", all_code, re.IGNORECASE)
        )

        # Mock R4R analysis
        analysis.r4r_dependencies = ["ggplot2", "dplyr", "tidyr", "readr", "purrr"]
        analysis.r4r_system_packages = ["libcurl", "libssl", "libxml2"]
        analysis.r4r_docker_ready = True

        # Calculate reproducibility score
        issues = sum(
            [
                not analysis.has_random_seed,
                analysis.has_hardcoded_paths,
                analysis.has_external_deps,
                analysis.has_time_deps,
                analysis.has_interactive_input,
            ]
        )

        analysis.r4r_reproducibility_score = max(0, 100 - (issues * 15))
        analysis.save()

        serializer = ReproducibilityAnalysisSerializer(analysis)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_docker(self, request, pk=None):
        """Generate Docker environment for notebook"""
        notebook = self.get_object()

        # Mock Docker generation
        dockerfile = f"""FROM rocker/r-ver:4.3.0

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libcurl4-openssl-dev \\
    libssl-dev \\
    libxml2-dev

# Install R packages
RUN R -e "install.packages(c('ggplot2', 'dplyr', 'tidyr', 'readr', 'purrr'))"

# Copy notebook
WORKDIR /notebook
COPY {notebook.title.replace(' ', '_')}.Rmd .

# Run notebook
CMD ["Rscript", "-e", "rmarkdown::render('{notebook.title.replace(' ', '_')}.Rmd')"]
"""

        return Response(
            {
                "dockerfile": dockerfile,
                "status": "success",
                "message": "Docker environment generated successfully",
            }
        )


class NotebookBlockViewSet(viewsets.ModelViewSet):
    serializer_class = NotebookBlockSerializer
    permission_classes = [AllowAny]  # For development

    def get_queryset(self):
        return NotebookBlock.objects.all()

    def perform_update(self, serializer):
        serializer.save()
