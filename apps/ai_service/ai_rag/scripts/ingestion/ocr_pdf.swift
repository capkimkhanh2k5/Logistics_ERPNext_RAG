import Foundation
import PDFKit
import Vision
import AppKit
import CryptoKit

let input = CommandLine.arguments[1]
let output = CommandLine.arguments[2]
let sourceData = try Data(contentsOf: URL(fileURLWithPath: input))
let sourceHash = SHA256.hash(data: sourceData).map { String(format: "%02x", $0) }.joined()
let document = PDFDocument(url: URL(fileURLWithPath: input))!
var pages: [[String: Any]] = []
let supported = try VNRecognizeTextRequest().supportedRecognitionLanguages()
let languages = ["vi-VN", "en-US"].filter { supported.contains($0) }
for index in 0..<document.pageCount {
    let page = document.page(at: index)!
    let bounds = page.bounds(for: .mediaBox)
    let size = NSSize(width: bounds.width * 3, height: bounds.height * 3)
    let image = page.thumbnail(of: size, for: .mediaBox)
    var rect = NSRect(origin: .zero, size: size)
    let cg = image.cgImage(forProposedRect: &rect, context: nil, hints: nil)!
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = languages
    request.usesLanguageCorrection = false
    try VNImageRequestHandler(cgImage: cg).perform([request])
    let lines: [[String: Any]] = (request.results ?? []).compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else { return nil }
        let box = observation.boundingBox
        return ["text": candidate.string, "confidence": candidate.confidence,
                "bbox": [box.origin.x, box.origin.y, box.width, box.height]]
    }
    pages.append(["physical_page": index + 1, "lines": lines])
    print("OCR page \(index + 1)/\(document.pageCount)")
}
let result: [String: Any] = ["pdf": input, "sha256": sourceHash, "engine": "Apple Vision", "languages": languages, "pages": pages]
try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys]).write(to: URL(fileURLWithPath: output))
