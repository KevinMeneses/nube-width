// Id de la ventana de REAPER cuyo título empieza con el texto dado (para capturarla con screencapture -l <id>
// sin traerla al frente). Con --bounds imprime "id x y ancho alto" (puntos).
//   swift tests/winid.swift ["JS: Nube Width"] [--bounds]
import CoreGraphics
let args = CommandLine.arguments.dropFirst()
let want = args.first { !$0.hasPrefix("--") } ?? "JS: Nube Width"
let list = CGWindowListCopyWindowInfo([.optionAll], kCGNullWindowID) as! [[String: Any]]
for w in list {
    let owner = w[kCGWindowOwnerName as String] as? String ?? ""
    let name = w[kCGWindowName as String] as? String ?? ""
    if owner.contains("REAPER") && name.hasPrefix(want) {
        let id = w[kCGWindowNumber as String] as! Int
        if args.contains("--bounds"), let b = w[kCGWindowBounds as String] as? [String: Any] {
            print(id, b["X"]!, b["Y"]!, b["Width"]!, b["Height"]!)
        } else { print(id) }
        break
    }
}
