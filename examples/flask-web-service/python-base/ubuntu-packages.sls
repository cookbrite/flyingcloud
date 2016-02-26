ubuntu.packages:
  pkg.latest:
    - fromrepo: trusty
    - pkgs:
      - gfortran
      - libfreetype6-dev
      - liblapack-dev
      - libopenblas-dev
      - libopencv-dev
      - libxft-dev
      - python-opencv
      - tesseract-ocr

# workaround for OpenCV trying to open nonexistent IEEE1394 device
/dev/raw1394:
  file.mknod:
    - ntype: c
    - major: 1
    - minor: 3
    - user: root
    - group: root
    - mode: 666
