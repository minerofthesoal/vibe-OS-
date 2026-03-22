#!/bin/bash
# Generate vibeOS default wallpaper using ImageMagick
# Run: bash generate-default.sh

if ! command -v magick &>/dev/null && ! command -v convert &>/dev/null; then
    echo "ImageMagick required. Install: sudo pacman -S imagemagick"
    exit 1
fi

OUTDIR="$(dirname "$0")"

CMD="magick"
if ! command -v magick &>/dev/null; then CMD="convert"; fi

# Generate 4K dark gradient wallpaper with subtle accent orbs
$CMD -size 3840x2160 \
    xc:'#0d1117' \
    \( -size 3840x2160 gradient:'#0d1117'-'#161b22' -rotate 45 \) -compose overlay -composite \
    \( -size 800x800 radial-gradient:'rgba(137,180,250,0.12)'-'rgba(0,0,0,0)' -geometry +2600+400 \) -compose over -composite \
    \( -size 600x600 radial-gradient:'rgba(203,166,247,0.08)'-'rgba(0,0,0,0)' -geometry +500+1400 \) -compose over -composite \
    \( -size 500x500 radial-gradient:'rgba(148,226,213,0.06)'-'rgba(0,0,0,0)' -geometry +1800+800 \) -compose over -composite \
    -blur 0x40 \
    "$OUTDIR/default.png"

echo "Generated: $OUTDIR/default.png"
