// Lifts every subject out of a photo with Apple's Vision framework (the same model as "Lift subject" in Photos).
// Writes one soft mask per instance as raw float32: <out>/mask-<n>-<w>x<h>.f32. blender/cutouts.py does the rest.
//   swiftc -O blender/lift.swift -o <bin>/lift && <bin>/lift photo.png <outdir>
import Foundation
import Vision

let args = CommandLine.arguments
let handler = VNImageRequestHandler(url: URL(fileURLWithPath: args[1]))
let request = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([request])
guard let result = request.results?.first else { print("no subject found"); exit(1) }
for i in result.allInstances {
    let buf = try result.generateScaledMaskForImage(forInstances: [i], from: handler)
    CVPixelBufferLockBaseAddress(buf, .readOnly)
    let w = CVPixelBufferGetWidth(buf), h = CVPixelBufferGetHeight(buf), row = CVPixelBufferGetBytesPerRow(buf)
    let base = CVPixelBufferGetBaseAddress(buf)!
    var data = Data(capacity: w * h * 4)
    for y in 0..<h { data.append(Data(bytes: base + y * row, count: w * 4)) }
    CVPixelBufferUnlockBaseAddress(buf, .readOnly)
    try data.write(to: URL(fileURLWithPath: args[2]).appendingPathComponent("mask-\(i)-\(w)x\(h).f32"))
}
print("instances: \(result.allInstances.count)")
