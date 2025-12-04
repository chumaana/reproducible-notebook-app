#!/usr/bin/env Rscript

cat('############################################################\n')
cat('# Starting installation...\n');
cat('############################################################\n')

options(Ncpus=min(parallel::detectCores(), 32))

dir.create('/tmp/r4r-lib', recursive=TRUE)
install.packages('remotes', lib = '/tmp/r4r-lib')
on.exit(unlink('/tmp/r4r-lib', recursive = TRUE))


cat('############################################################\n')
cat('# Installing batch 1/8 with 6 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('R6', '2.6.1', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-R6-2.6.1.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('base64enc', '0.1-3', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-base64enc-0.1-3.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('evaluate', '1.0.5', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-evaluate-1.0.5.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('fastmap', '1.2.0', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-fastmap-1.2.0.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('rappdirs', '0.3.3', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-rappdirs-0.3.3.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('yaml', '2.3.10', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-yaml-2.3.10.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 1/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package R6 version 2.6.1 (/tmp/r4r-install-R6-2.6.1.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-R6-2.6.1.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package base64enc version 0.1-3 (/tmp/r4r-install-base64enc-0.1-3.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-base64enc-0.1-3.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package evaluate version 1.0.5 (/tmp/r4r-install-evaluate-1.0.5.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-evaluate-1.0.5.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package fastmap version 1.2.0 (/tmp/r4r-install-fastmap-1.2.0.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-fastmap-1.2.0.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package rappdirs version 0.3.3 (/tmp/r4r-install-rappdirs-0.3.3.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-rappdirs-0.3.3.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package yaml version 2.3.10 (/tmp/r4r-install-yaml-2.3.10.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-yaml-2.3.10.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'R6'
  pkg_ver  <- '2.6.1'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-R6-2.6.1.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'base64enc'
  pkg_ver  <- '0.1-3'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-base64enc-0.1-3.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'evaluate'
  pkg_ver  <- '1.0.5'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-evaluate-1.0.5.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'fastmap'
  pkg_ver  <- '1.2.0'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-fastmap-1.2.0.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'rappdirs'
  pkg_ver  <- '0.3.3'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-rappdirs-0.3.3.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'yaml'
  pkg_ver  <- '2.3.10'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-yaml-2.3.10.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 2/8 with 4 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('cli', '3.6.5', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-cli-3.6.5.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('digest', '0.6.39', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-digest-0.6.39.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('mime', '0.13', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-mime-0.13.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('rlang', '1.1.6', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-rlang-1.1.6.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 2/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package cli version 3.6.5 (/tmp/r4r-install-cli-3.6.5.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-cli-3.6.5.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package digest version 0.6.39 (/tmp/r4r-install-digest-0.6.39.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-digest-0.6.39.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package mime version 0.13 (/tmp/r4r-install-mime-0.13.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-mime-0.13.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package rlang version 1.1.6 (/tmp/r4r-install-rlang-1.1.6.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-rlang-1.1.6.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'cli'
  pkg_ver  <- '3.6.5'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-cli-3.6.5.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'digest'
  pkg_ver  <- '0.6.39'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-digest-0.6.39.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'mime'
  pkg_ver  <- '0.13'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-mime-0.13.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'rlang'
  pkg_ver  <- '1.1.6'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-rlang-1.1.6.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 3/8 with 2 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('cachem', '1.1.0', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-cachem-1.1.0.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('htmltools', '0.5.8.1', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-htmltools-0.5.8.1.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 3/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package cachem version 1.1.0 (/tmp/r4r-install-cachem-1.1.0.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-cachem-1.1.0.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package htmltools version 0.5.8.1 (/tmp/r4r-install-htmltools-0.5.8.1.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-htmltools-0.5.8.1.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'cachem'
  pkg_ver  <- '1.1.0'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-cachem-1.1.0.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'htmltools'
  pkg_ver  <- '0.5.8.1'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-htmltools-0.5.8.1.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 4/8 with 4 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('fontawesome', '0.5.3', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-fontawesome-0.5.3.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('jquerylib', '0.1.4', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-jquerylib-0.1.4.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('memoise', '2.0.1', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-memoise-2.0.1.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('xfun', '0.54', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-xfun-0.54.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 4/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package fontawesome version 0.5.3 (/tmp/r4r-install-fontawesome-0.5.3.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-fontawesome-0.5.3.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package jquerylib version 0.1.4 (/tmp/r4r-install-jquerylib-0.1.4.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-jquerylib-0.1.4.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package memoise version 2.0.1 (/tmp/r4r-install-memoise-2.0.1.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-memoise-2.0.1.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package xfun version 0.54 (/tmp/r4r-install-xfun-0.54.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-xfun-0.54.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'fontawesome'
  pkg_ver  <- '0.5.3'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-fontawesome-0.5.3.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'jquerylib'
  pkg_ver  <- '0.1.4'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-jquerylib-0.1.4.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'memoise'
  pkg_ver  <- '2.0.1'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-memoise-2.0.1.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'xfun'
  pkg_ver  <- '0.54'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-xfun-0.54.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 5/8 with 5 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('fs', '1.6.6', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-fs-1.6.6.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('glue', '1.8.0', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-glue-1.8.0.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('highr', '0.11', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-highr-0.11.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('jsonlite', '2.0.0', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-jsonlite-2.0.0.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('tinytex', '0.58', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-tinytex-0.58.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 5/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package fs version 1.6.6 (/tmp/r4r-install-fs-1.6.6.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-fs-1.6.6.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package glue version 1.8.0 (/tmp/r4r-install-glue-1.8.0.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-glue-1.8.0.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package highr version 0.11 (/tmp/r4r-install-highr-0.11.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-highr-0.11.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package jsonlite version 2.0.0 (/tmp/r4r-install-jsonlite-2.0.0.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-jsonlite-2.0.0.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package tinytex version 0.58 (/tmp/r4r-install-tinytex-0.58.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-tinytex-0.58.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'fs'
  pkg_ver  <- '1.6.6'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-fs-1.6.6.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'glue'
  pkg_ver  <- '1.8.0'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-glue-1.8.0.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'highr'
  pkg_ver  <- '0.11'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-highr-0.11.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'jsonlite'
  pkg_ver  <- '2.0.0'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-jsonlite-2.0.0.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'tinytex'
  pkg_ver  <- '0.58'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-tinytex-0.58.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 6/8 with 3 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('knitr', '1.50', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-knitr-1.50.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('lifecycle', '1.0.4', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-lifecycle-1.0.4.log 2>&1 & Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('sass', '0.4.10', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-sass-0.4.10.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 6/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package knitr version 1.50 (/tmp/r4r-install-knitr-1.50.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-knitr-1.50.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package lifecycle version 1.0.4 (/tmp/r4r-install-lifecycle-1.0.4.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-lifecycle-1.0.4.log'), sep='\n')
  cat('\n')
  cat('############################################################\n')
  cat('# Logs for package sass version 0.4.10 (/tmp/r4r-install-sass-0.4.10.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-sass-0.4.10.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'knitr'
  pkg_ver  <- '1.50'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-knitr-1.50.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'lifecycle'
  pkg_ver  <- '1.0.4'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-lifecycle-1.0.4.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

{
  pkg_name <- 'sass'
  pkg_ver  <- '0.4.10'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-sass-0.4.10.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 7/8 with 1 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('bslib', '0.9.0', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-bslib-0.9.0.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 7/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package bslib version 0.9.0 (/tmp/r4r-install-bslib-0.9.0.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-bslib-0.9.0.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'bslib'
  pkg_ver  <- '0.9.0'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-bslib-0.9.0.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# Installing batch 8/8 with 1 packages...\n');
cat('############################################################\n')

status <- system("Rscript -e \"require('remotes', lib.loc = '/tmp/r4r-lib');remotes::install_version('rmarkdown', '2.30', upgrade = 'never', dependencies = FALSE)
\" > /tmp/r4r-install-rmarkdown-2.30.log 2>&1 & wait")
if (status != 0) {
  cat('############################################################\n')
  cat('# Batch 8/8 FAILED.\n');
    cat('############################################################\n')

  cat('############################################################\n')
  cat('# Logs for package rmarkdown version 2.30 (/tmp/r4r-install-rmarkdown-2.30.log)\n');
  cat('############################################################\n')
  cat(readLines('/tmp/r4r-install-rmarkdown-2.30.log'), sep='\n')
  cat('\n')
  quit(status = 1)
}

{
  pkg_name <- 'rmarkdown'
  pkg_ver  <- '2.30'
  installed_ver <- tryCatch(as.character(packageVersion(pkg_name)), error = function(e) NA)
  if (is.na(installed_ver)) {
    cat('############################################################\n')
    cat('# Error: Failed to install ', pkg_name, ' ', pkg_ver, '\n');
    cat('############################################################\n')
    cat(readLines('/tmp/r4r-install-rmarkdown-2.30.log'), sep='\n')
    cat('\n')
    quit(status = 1)
} else if (installed_ver != pkg_ver) {
    cat('############################################################\n')
    cat('# Warning: Different version of ', pkg_name, ' installed. Expected: ', pkg_ver, ', installed: ', installed_ver, '\n');
    cat('############################################################\n')
  }
}

cat('############################################################\n')
cat('# All 26 packages installed successfully.\n');
cat('############################################################\n')
