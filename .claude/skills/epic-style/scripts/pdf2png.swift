// Render every page of a PDF to PNG with PDFKit (no poppler/mutool on this Mac).
// Usage: swift pdf2png.swift <in.pdf> <out_dir> <scale>   -> out_dir/itin-p1.png, itin-p2.png ...
// Scale 5 keeps web-page text crisp after the 3D tilt zoom.
import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
let doc = PDFDocument(url: URL(fileURLWithPath: args[1]))!
let scale = CGFloat(Double(args[3])!)
for i in 0..<doc.pageCount {
  let page = doc.page(at: i)!
  let r = page.bounds(for: .mediaBox)
  let w = Int(r.width * scale), h = Int(r.height * scale)
  let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8, samplesPerPixel: 4,
                             hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
  let ctx = NSGraphicsContext(bitmapImageRep: rep)!
  NSGraphicsContext.current = ctx
  let cg = ctx.cgContext
  cg.setFillColor(NSColor.white.cgColor); cg.fill(CGRect(x: 0, y: 0, width: w, height: h))
  cg.scaleBy(x: scale, y: scale); cg.translateBy(x: -r.origin.x, y: -r.origin.y)
  page.draw(with: .mediaBox, to: cg)
  ctx.flushGraphics()
  let data = rep.representation(using: .png, properties: [:])!
  try! data.write(to: URL(fileURLWithPath: "\(args[2])/itin-p\(i+1).png"))
  print(i + 1, w, h)
}
