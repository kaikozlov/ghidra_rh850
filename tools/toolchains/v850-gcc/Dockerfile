# Rebuild the GNU V850/RH850 toolchain used by the public Toyota payload lineage.
# Source commits are the immutable release tags behind the historical
# binutils-2_41-release / releases/gcc-13.2.0 recipe.
ARG UBUNTU_IMAGE=ubuntu@sha256:b8b6ee6aa931ecd9d0d952abc34dc0e5f7c6a30c6bb71b079fe399fde0329c02

FROM ${UBUNTU_IMAGE} AS build

ARG TARGET_ARCH=v850-elf
ARG BINUTILS_GDB_COMMIT=675b9d612cc59446e84e2c6d89b45500cb603a8d
ARG GCC_COMMIT=c891d8dc23e1a46ad9f3e757d09e57b500d40044
ENV TOOLCHAIN_PATH=/opt/gcc-v850-elf-master
ENV PATH="${TOOLCHAIN_PATH}/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential bison ca-certificates flex git libgmp3-dev libmpc-dev libmpfr-dev texinfo \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth=1 --branch=binutils-2_41-release \
      https://sourceware.org/git/binutils-gdb.git \
 && test "$(git -C binutils-gdb rev-parse HEAD)" = "${BINUTILS_GDB_COMMIT}"

WORKDIR /build/binutils
RUN /src/binutils-gdb/configure \
      --target="${TARGET_ARCH}" \
      --prefix="${TOOLCHAIN_PATH}" \
      --disable-nls \
 && make -j"$(nproc)" all \
 && make install

WORKDIR /src
RUN git clone --depth=1 --branch=releases/gcc-13.2.0 \
      https://gcc.gnu.org/git/gcc.git \
 && test "$(git -C gcc rev-parse HEAD)" = "${GCC_COMMIT}"

WORKDIR /build/gcc
RUN /src/gcc/configure \
      --target="${TARGET_ARCH}" \
      --prefix="${TOOLCHAIN_PATH}" \
      --disable-nls \
      --enable-languages=c \
      --without-headers \
      --with-gnu-as \
      --with-gnu-ld \
      --disable-shared \
      --disable-libssp \
      --disable-threads \
      --with-newlib \
 && make -j"$(nproc)" all-gcc \
 && make install-gcc

FROM ${UBUNTU_IMAGE}

ENV TOOLCHAIN_PATH=/opt/gcc-v850-elf-master
ENV PATH="${TOOLCHAIN_PATH}/bin:${PATH}"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgmp10 libmpc3 libmpfr6 libstdc++6 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/gcc-v850-elf-master /opt/gcc-v850-elf-master

LABEL org.opencontainers.image.title="ghidra_rh850 GNU V850/RH850 toolchain"
LABEL org.opencontainers.image.description="GCC 13.2.0 + binutils/GDB 2.41 lineage with the compiled-in V850/RH850 simulator"
LABEL org.opencontainers.image.source="https://github.com/kaikozlov/ghidra_rh850"

WORKDIR /src
CMD ["/bin/bash"]
