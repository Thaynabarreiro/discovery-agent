// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "DiscoveryAgentLauncher",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "Discovery Agent Launcher", targets: ["DiscoveryAgentLauncher"])
    ],
    targets: [
        .executableTarget(
            name: "DiscoveryAgentLauncher",
            path: "Sources"
        )
    ]
)
