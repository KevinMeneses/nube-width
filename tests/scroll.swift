// Rueda del mouse en la posición actual: swift tests/scroll.swift <líneas> (positivo = arriba)
import CoreGraphics
let n = Int32(CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "1") ?? 1
for _ in 0..<abs(n) {
    CGEvent(scrollWheelEvent2Source: nil, units: .line, wheelCount: 1, wheel1: n > 0 ? 1 : -1, wheel2: 0, wheel3: 0)?.post(tap: .cghidEventTap)
    usleep(30000)
}
