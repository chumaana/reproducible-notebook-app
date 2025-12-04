FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

ENV LANG=en_US.UTF-8

ENV TZ=UTC

RUN apt-get update -y && \
  apt-get install -y --no-install-recommends locales tzdata && \
  echo $LANG >> /etc/locale.gen && \
  locale-gen $LANG && \
  update-locale LANG=$LANG

RUN id ubuntu &>/dev/null && userdel -r ubuntu && \
  groupadd -g 1000 pitopl && \
  (groupadd -g 1000 pitopl || groupmod -g 1000 pitopl) && \
  (groupadd -g 4 adm || groupmod -g 4 adm) && \
  (groupadd -g 24 cdrom || groupmod -g 24 cdrom) && \
  (groupadd -g 27 sudo || groupmod -g 27 sudo) && \
  (groupadd -g 30 dip || groupmod -g 30 dip) && \
  (groupadd -g 46 plugdev || groupmod -g 46 plugdev) && \
  (groupadd -g 100 users || groupmod -g 100 users) && \
  (groupadd -g 114 lpadmin || groupmod -g 114 lpadmin) && \
  (groupadd -g 984 docker || groupmod -g 984 docker) && \
  useradd -u 1000 -g 1000 -G adm,cdrom,dip,docker,lpadmin,pitopl,plugdev,sudo,users -d /home/pitopl -s /bin/bash pitopl && \
  mkdir -p /home/pitopl && \
  chown pitopl:pitopl /home/pitopl && \
  apt-get update -y && \
  apt-get install -y sudo && \
  echo 'pitopl ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/pitopl && \
  chmod 0440 /etc/sudoers.d/pitopl

RUN apt-get update -y && \
  apt-get install -y --no-install-recommends base-files=13ubuntu10.2 \
      libblas3:amd64=3.12.0-3build1.1 \
      libbrotli1:amd64=1.1.0-2build2 \
      libbsd0:amd64=0.12.1-1build1.1 \
      libcairo2:amd64=1.18.0-3build1 \
      libdatrie1:amd64=0.2.13-3build1 \
      libdeflate0:amd64=1.19-1build1.1 \
      libexpat1:amd64=2.6.1-2ubuntu0.3 \
      libfontconfig1:amd64=2.15.0-1.1ubuntu2 \
      libfreetype6:amd64=2.13.2+dfsg-1build3 \
      libfribidi0:amd64=1.0.13-3build1 \
      libgfortran5:amd64=14.2.0-4ubuntu2~24.04 \
      libglib2.0-0t64:amd64=2.80.0-6ubuntu3.4 \
      libgomp1:amd64=14.2.0-4ubuntu2~24.04 \
      libgraphite2-3:amd64=1.3.14-2build1 \
      libgssapi-krb5-2:amd64=1.20.1-6ubuntu2.6 \
      libharfbuzz0b:amd64=8.3.0-2build2 \
      libice6:amd64=2:1.0.10-1build3 \
      libicu74:amd64=74.2-1ubuntu3.1 \
      libjbig0:amd64=2.1-6.1ubuntu2 \
      libjpeg-turbo8:amd64=2.1.5-2ubuntu2 \
      libk5crypto3:amd64=1.20.1-6ubuntu2.6 \
      libkeyutils1:amd64=1.6.3-3build1 \
      libkrb5-3:amd64=1.20.1-6ubuntu2.6 \
      libkrb5support0:amd64=1.20.1-6ubuntu2.6 \
      liblapack3:amd64=3.12.0-3build1.1 \
      liblerc4:amd64=4.0.0+ds-4ubuntu2 \
      liblua5.4-0:amd64=5.4.6-3build2 \
      libpango-1.0-0:amd64=1.52.1+ds-1build1 \
      libpangocairo-1.0-0:amd64=1.52.1+ds-1build1 \
      libpangoft2-1.0-0:amd64=1.52.1+ds-1build1 \
      libpixman-1-0:amd64=0.42.2-1build1 \
      libpng16-16t64:amd64=1.6.43-5build1 \
      libreadline8t64:amd64=8.2-4build1 \
      libsharpyuv0:amd64=1.3.2-0.4build3 \
      libsm6:amd64=2:1.2.3-1build3 \
      libthai0:amd64=0.1.29-2build1 \
      libtiff6:amd64=4.5.1+git230720-4ubuntu2.4 \
      libtirpc3t64:amd64=1.3.4+ds-1.1build1 \
      libwebp7:amd64=1.3.2-0.4build3 \
      libx11-6:amd64=2:1.8.7-1build1 \
      libxau6:amd64=1:1.0.9-1build6 \
      libxcb-render0:amd64=1.15-1ubuntu2 \
      libxcb-shm0:amd64=1.15-1ubuntu2 \
      libxcb1:amd64=1.15-1ubuntu2 \
      libxdmcp6:amd64=1:1.1.3-0ubuntu6 \
      libxext6:amd64=2:1.3.4-1build2 \
      libxrender1:amd64=1:0.9.10-1.1build1 \
      libxt6t64:amd64=1:1.2.1-1.2build1 \
      libyaml-0-2:amd64=0.2.5-1build1 \
      locales=2.39-0ubuntu8.6 \
      make=4.3-4.1build2 \
      pandoc-data=3.1.3-1 \
      pandoc=3.1.3+ds-2 \
      r-base-core=4.3.3-2build2 \
      r-base-dev=4.3.3-2build2 \
      r-cran-kernsmooth=2.23-22-1build1 \
      systemd-oomd=255.4-1ubuntu8.8

COPY install_r_packages.R /

RUN Rscript /install_r_packages.R && \
  rm -f /install_r_packages.R

COPY pre_file_copy.sh ./pre_file_copy.sh

RUN bash "./pre_file_copy.sh" && \
  rm -f "./pre_file_copy.sh"

COPY archive.tar ./archive.tar

RUN tar -x -f "./archive.tar" --same-owner --same-permissions --absolute-names && \
  rm -f "./archive.tar"

COPY post_file_copy.sh ./post_file_copy.sh

RUN bash "./post_file_copy.sh" && \
  rm -f "./post_file_copy.sh"

ENV BUNDLED_DEBUGPY_PATH=/home/pitopl/.vscode/extensions/ms-python.debugpy-2025.16.0-linux-x64/bundled/libs/debugpy \
  CHROME_DESKTOP=code.desktop \
  CLUTTER_DISABLE_MIPMAPPED_TEXT=1 \
  COLORTERM=truecolor \
  CONDA_PROMPT_MODIFIER=false \
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  DEBUGINFOD_URLS='https://debuginfod.ubuntu.com ' \
  DESKTOP_SESSION=ubuntu \
  DISPLAY=:0 \
  DJANGO_SETTINGS_MODULE=notebook_api.settings \
  GDK_BACKEND=x11 \
  GDMSESSION=ubuntu \
  GIO_LAUNCHED_DESKTOP_FILE=/usr/share/applications/code.desktop \
  GIO_LAUNCHED_DESKTOP_FILE_PID=101259 \
  GIT_ASKPASS=/usr/share/code/resources/app/extensions/git/dist/askpass.sh \
  GJS_DEBUG_OUTPUT=stderr \
  GJS_DEBUG_TOPICS='JS ERROR;JS LOG' \
  GNOME_DESKTOP_SESSION_ID=this-is-deprecated \
  GNOME_SETUP_DISPLAY=:1 \
  GNOME_SHELL_SESSION_MODE=ubuntu \
  GSM_SKIP_SSH_AGENT_WORKAROUND=true \
  GTK_MODULES=gail:atk-bridge \
  IM_CONFIG_CHECK_ENV=1 \
  IM_CONFIG_PHASE=1 \
  INVOCATION_ID=18db4896a74f4450b420e39e3b009fc0 \
  JOURNAL_STREAM=9:9899 \
  LANG=en_US.UTF-8 \
  LESSCLOSE='/usr/bin/lesspipe %s %s' \
  LESSOPEN='| /usr/bin/lesspipe %s' \
  LS_COLORS='rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:' \
  MANAGERPID=1522 \
  MEMORY_PRESSURE_WATCH=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/session.slice/org.gnome.Shell@wayland.service/memory.pressure \
  MEMORY_PRESSURE_WRITE=c29tZSAyMDAwMDAgMjAwMDAwMAA= \
  NVM_BIN=/home/pitopl/.nvm/versions/node/v22.15.0/bin \
  NVM_CD_FLAGS= \
  NVM_DIR=/home/pitopl/.nvm \
  NVM_INC=/home/pitopl/.nvm/versions/node/v22.15.0/include/node \
  ORIGINAL_XDG_CURRENT_DESKTOP=ubuntu:GNOME \
  OSTYPE=linux-gnu \
  PATH=/home/pitopl/Desktop/thesis/reproducible-notebook-app/backend/venv/bin:/home/pitopl/.local/bin:/home/pitopl/.nvm/versions/node/v22.15.0/bin:/home/pitopl/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/pitopl/.vscode/extensions/ms-python.debugpy-2025.16.0-linux-x64/bundled/scripts/noConfigScripts \
  POSH_SESSION_ID=d2c67ec3-b859-4fe5-9461-e3800e5fd300 \
  POSH_SHELL=bash \
  POSH_SHELL_VERSION='5.2.21(1)-release' \
  POSH_THEME=/home/pitopl/.cache/oh-my-posh/config.2d317612584924d81d33eaaf87ae1579ef713e9f2899dc297393d1dedbae3ead.omp.json \
  POWERLINE_COMMAND=oh-my-posh \
  PYDEVD_DISABLE_FILE_VALIDATION=1 \
  PYENV_VIRTUALENV_DISABLE_PROMPT=1 \
  PYTHONSTARTUP=/home/pitopl/.config/Code/User/workspaceStorage/c89cd9d88fc80126e70011877036fda0/ms-python.python/pythonrc.py \
  PYTHON_BASIC_REPL=1 \
  QT_ACCESSIBILITY=1 \
  QT_IM_MODULE=ibus \
  RUN_MAIN=true \
  SESSION_MANAGER=local/pitopl-Redmi-Book-Pro-14-2024:@/tmp/.ICE-unix/1741,unix/pitopl-Redmi-Book-Pro-14-2024:/tmp/.ICE-unix/1741 \
  SHELL=/bin/bash \
  SHLVL=1 \
  SYSTEMD_EXEC_PID=1784 \
  TERM=xterm-256color \
  TERM_PROGRAM=vscode \
  TERM_PROGRAM_VERSION=1.98.2 \
  TZ=UTC \
  USERNAME=pitopl \
  VIRTUAL_ENV=/home/pitopl/Desktop/thesis/reproducible-notebook-app/backend/venv \
  VIRTUAL_ENV_DISABLE_PROMPT=1 \
  VSCODE_DEBUGPY_ADAPTER_ENDPOINTS=/home/pitopl/.vscode/extensions/ms-python.debugpy-2025.16.0-linux-x64/.noConfigDebugAdapterEndpoints/endpoint-6de526d813409550.txt \
  VSCODE_GIT_ASKPASS_EXTRA_ARGS= \
  VSCODE_GIT_ASKPASS_MAIN=/usr/share/code/resources/app/extensions/git/dist/askpass-main.js \
  VSCODE_GIT_ASKPASS_NODE=/usr/share/code/code \
  VSCODE_GIT_IPC_HANDLE=/run/user/1000/vscode-git-6120bd3ae8.sock \
  WAYLAND_DISPLAY=wayland-0 \
  XAUTHORITY=/run/user/1000/.mutter-Xwaylandauth.07SCG3 \
  XDG_CONFIG_DIRS=/etc/xdg/xdg-ubuntu:/etc/xdg \
  XDG_CURRENT_DESKTOP=Unity \
  XDG_DATA_DIRS=/usr/share/ubuntu:/usr/share/gnome:/usr/local/share/:/usr/share/:/var/lib/snapd/desktop \
  XDG_MENU_PREFIX=gnome- \
  XDG_SESSION_DESKTOP=ubuntu \
  XMODIFIERS=@im=ibus \
  _=/home/pitopl/Desktop/thesis/reproducible-notebook-app/backend/venv/bin/python

RUN mkdir -p "/home/pitopl/Desktop/thesis/reproducible-notebook-app/backend" && \
  chown pitopl:pitopl "/home/pitopl/Desktop/thesis/reproducible-notebook-app/backend"

WORKDIR /home/pitopl/Desktop/thesis/reproducible-notebook-app/backend

USER pitopl

RUN R -e 'dir.create(unlist(strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep))[1L], recursive=TRUE)'

CMD ["R", "-e", "rmarkdown::render(\"/tmp/tmp3zcmrji6/notebook.Rmd\")", "--output", "/tmp/tmp3zcmrji6/output", "--result", "notebook.html", "--docker-image-tag", "notebook-9", "--docker-container-name", "notebook-container-9", "--skip-make"]

