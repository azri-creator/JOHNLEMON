# Sharp full-screen tilt planes from PDF screenshots: take the EMBEDDED raster (pypdf), never a sips/pdftoppm
# rasterisation (that came out soft). Usage: /usr/bin/python3 pdf_tilt.py in.pdf out.jpg ROW0 [W H] [X0 X1]
#   16:9 plane: 2420x1546 of a 3456x2207 crop.  9:16 plane: 2312x2050 of columns 691..3180 (content column).
import sys, pypdf, cv2, numpy as np
pdf, out, r0 = sys.argv[1], sys.argv[2], int(sys.argv[3])
W, H = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (2420, 1546)
x0, x1 = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (0, None)
im = pypdf.PdfReader(pdf).pages[0].images[0]
a = cv2.imdecode(np.frombuffer(im.data, np.uint8), cv2.IMREAD_COLOR)
rows = round(2207 * (a.shape[1] / 3456))                 # keep the 3456x2207 window ratio
a = a[r0:r0 + rows, x0:x1]
cv2.imwrite(out, cv2.resize(a, (W, H), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 95])
print(out, a.shape, '->', (W, H))
