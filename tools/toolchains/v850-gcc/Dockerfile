# The single pinned GNU V850/RH850 toolchain used by tools/rh850.
ARG UBUNTU_IMAGE=ubuntu@sha256:da6fc2be547864451aa253836dd926da33623312df4a9a243e35dc877c378a78
FROM ${UBUNTU_IMAGE} AS build
ARG TARGET_ARCH=v850-elf
ARG BINUTILS_COMMIT=5e56594815854de5eca35c7c04b11705d0f19c02
ARG GDB_COMMIT=6a5e5259790e5a854ddbb69eb486b9245fcfeee8
ENV TOOLCHAIN_PATH=/opt/gcc-v850-elf-master
ENV PATH="${TOOLCHAIN_PATH}/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential bison ca-certificates flex git libexpat1-dev libgmp-dev libmpc-dev libmpfr-dev texinfo \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /src
RUN git clone --depth=1 --branch=binutils-2_46_1 https://sourceware.org/git/binutils-gdb.git binutils \
 && test "$(git -C binutils rev-parse HEAD)" = "${BINUTILS_COMMIT}"
WORKDIR /build/binutils
RUN /src/binutils/configure --target="${TARGET_ARCH}" --prefix="${TOOLCHAIN_PATH}" --disable-nls \
      --disable-gdb --disable-gdbserver --disable-sim --disable-werror \
 && make -j"$(nproc)" all && make install
WORKDIR /src
COPY patches/binutils-v850-sim-imm32.patch /tmp/binutils-v850-sim-imm32.patch
RUN git clone --depth=1 --branch=gdb-18.1-release https://sourceware.org/git/binutils-gdb.git gdb \
 && test "$(git -C gdb rev-parse HEAD)" = "${GDB_COMMIT}" \
 && git -C gdb apply --check /tmp/binutils-v850-sim-imm32.patch \
 && git -C gdb apply /tmp/binutils-v850-sim-imm32.patch
WORKDIR /build/gdb
RUN /src/gdb/configure --target="${TARGET_ARCH}" --prefix="${TOOLCHAIN_PATH}" --disable-nls --disable-werror \
      --disable-binutils --disable-gas --disable-gprof --disable-gprofng --disable-ld --disable-gold --disable-gdbserver \
 && make -j"$(nproc)" all-gdb all-sim \
 && make install-gdb install-sim
WORKDIR /src
ARG GCC_REF=releases/gcc-16.2.0
ARG GCC_COMMIT=78d4ac73dd391005b895a6148cd9831e28e1208b
RUN test -n "${GCC_REF}" && test -n "${GCC_COMMIT}" \
 && git clone --depth=1 --branch="${GCC_REF}" https://gcc.gnu.org/git/gcc.git gcc \
 && test "$(git -C gcc rev-parse HEAD)" = "${GCC_COMMIT}"
WORKDIR /build/gcc
RUN /src/gcc/configure --target="${TARGET_ARCH}" --prefix="${TOOLCHAIN_PATH}" --disable-nls --enable-languages=c \
      --without-headers --with-gnu-as --with-gnu-ld --disable-shared --disable-libssp --disable-threads --with-newlib \
 && make -j"$(nproc)" all-gcc && make install-gcc
FROM ${UBUNTU_IMAGE}
ENV TOOLCHAIN_PATH=/opt/gcc-v850-elf-master
ENV PATH="${TOOLCHAIN_PATH}/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  libexpat1 libgmp10 libmpc3 libmpfr6 libstdc++6 \
  && rm -rf /var/lib/apt/lists/*
COPY --from=build /opt/gcc-v850-elf-master /opt/gcc-v850-elf-master
WORKDIR /src
CMD ["/bin/bash"]

LABEL org.opencontainers.image.title="ghidra_rh850 GNU V850/RH850 toolchain"
LABEL org.opencontainers.image.description="GNU C compiler, binutils and GDB with the repository-local V850/RH850 imm32 simulator fix"
LABEL org.opencontainers.image.source="https://github.com/kaikozlov/ghidra_rh850"
