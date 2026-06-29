{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.requests
    pkgs.python3Packages.pillow
    pkgs.nodejs
  ];
}
