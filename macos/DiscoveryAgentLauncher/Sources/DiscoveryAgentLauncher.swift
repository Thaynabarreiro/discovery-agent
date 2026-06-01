import AppKit
import SwiftUI

private let projectDirectory = "/Users/thaynamartinsbarreiro/Documents/IA para PMEs — AI Agency/02_Prospecção/00_ Discovery Call/discovery-agent"
private let pythonPath = "\(projectDirectory)/.venv/bin/python"
private let actionScriptPath = "\(projectDirectory)/scripts/dock_launcher_action.py"

@main
struct DiscoveryAgentLauncherApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate

    var body: some Scene {
        WindowGroup {
            LauncherView()
                .frame(width: 520, height: 610)
                .background(WindowAccessor())
        }
        .windowStyle(.hiddenTitleBar)
        .windowResizability(.contentSize)
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        NSApp.activate(ignoringOtherApps: true)
    }
}

struct LauncherView: View {
    @State private var mode: LauncherMode = .live
    @State private var clientName = ""
    @State private var sessionType = "Discovery Call"
    @State private var usesHeadphones = false
    @State private var sessionId = UserDefaults.standard.string(forKey: "DiscoveryAgentLastSessionId") ?? ""
    @State private var isRecording = UserDefaults.standard.bool(forKey: "DiscoveryAgentIsRecording")
    @State private var transcriptMode: TranscriptMode = .paste
    @State private var transcriptText = ""
    @State private var transcriptPath = ""
    @State private var isRunning = false
    @State private var statusTitle = "Ready"
    @State private var statusMessage = "Choose a mode to start."

    private let sessionTypes = ["Discovery Call", "Interview", "Internal Meeting", "Other"]

    var body: some View {
        ZStack {
            VisualEffectView(material: .hudWindow, blendingMode: .behindWindow)
                .ignoresSafeArea()
                .allowsHitTesting(false)

            LinearGradient(
                colors: [
                    Color.white.opacity(0.28),
                    Color(red: 0.78, green: 0.88, blue: 1.0).opacity(0.18),
                    Color(red: 1.0, green: 0.72, blue: 0.62).opacity(0.12)
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            .allowsHitTesting(false)

            GlassPanel {
                VStack(alignment: .leading, spacing: 20) {
                    header
                    modePicker

                    Group {
                        switch mode {
                        case .live:
                            liveControls
                        case .transcript:
                            transcriptControls
                        case .stop:
                            stopControls
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)

                    statusPanel
                }
                .padding(26)
            }
            .padding(22)
        }
    }

    private var header: some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 5) {
                Text("Discovery Agent")
                    .font(.system(size: 30, weight: .semibold, design: .rounded))
                Text("Live capture and transcript processing")
                    .font(.system(size: 13, weight: .medium))
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Image(systemName: "sparkles")
                .font(.system(size: 22, weight: .semibold))
                .symbolRenderingMode(.hierarchical)
                .foregroundStyle(.primary)
                .padding(12)
                .background(.ultraThinMaterial, in: Circle())
        }
    }

    private var modePicker: some View {
        HStack(spacing: 10) {
            ModeButton(title: "Live", systemImage: "waveform.circle.fill", isSelected: mode == .live) {
                mode = .live
            }
            ModeButton(title: "Stop", systemImage: "stop.circle.fill", isSelected: mode == .stop) {
                mode = .stop
            }
            ModeButton(title: "Transcript", systemImage: "doc.text.fill", isSelected: mode == .transcript) {
                mode = .transcript
            }
        }
    }

    private var liveControls: some View {
        VStack(alignment: .leading, spacing: 14) {
            TextField("Client or company name", text: $clientName)
                .textFieldStyle(.roundedBorder)

            Picker("Session type", selection: $sessionType) {
                ForEach(sessionTypes, id: \.self) { Text($0) }
            }
            .pickerStyle(.segmented)

            Toggle(isOn: $usesHeadphones) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Using headphones in an online call")
                    Text("Turn this on only when you need to capture call audio through BlackHole. Leave it off to test with your microphone.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .toggleStyle(.switch)

            PrimaryButton(title: isRecording ? "Recording Started" : "Start Recording", systemImage: "record.circle") {
                startLiveCall()
            }
            .disabled(isRecording || isRunning)
            .opacity((isRecording || isRunning) ? 0.65 : 1)
        }
    }

    private var stopControls: some View {
        VStack(alignment: .leading, spacing: 14) {
            TextField("Current session ID", text: $sessionId)
                .textFieldStyle(.roundedBorder)

            Text(isRecording ? "Recording is active. Stop will finalize transcription and generate the outputs." : "No active recording is marked in this launcher. If you started from another window, paste the session ID here.")
                .font(.caption)
                .foregroundStyle(.secondary)

            PrimaryButton(title: "Stop Recording and Generate Outputs", systemImage: "stop.fill") {
                stopLiveCall()
            }
            .disabled(sessionId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isRunning)
            .opacity((sessionId.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isRunning) ? 0.65 : 1)
        }
    }

    private var transcriptControls: some View {
        VStack(alignment: .leading, spacing: 14) {
            Picker("Transcript input", selection: $transcriptMode) {
                Text("Choose File").tag(TranscriptMode.file)
                Text("Paste Text").tag(TranscriptMode.paste)
            }
            .pickerStyle(.segmented)

            if transcriptMode == .file {
                HStack(spacing: 10) {
                    Text(transcriptPath.isEmpty ? "No file selected" : transcriptPath)
                        .lineLimit(1)
                        .truncationMode(.middle)
                        .font(.system(size: 12))
                        .foregroundStyle(.secondary)
                        .frame(maxWidth: .infinity, alignment: .leading)

                    Button("Choose") {
                        chooseTranscriptFile()
                    }
                }
                .padding(12)
                .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            } else {
                TextEditor(text: $transcriptText)
                    .font(.system(size: 13))
                    .scrollContentBackground(.hidden)
                    .frame(height: 150)
                    .padding(8)
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(Color.white.opacity(0.34), lineWidth: 1)
                            .allowsHitTesting(false)
                    )
            }

            PrimaryButton(title: "Process Transcript", systemImage: "arrow.up.doc.fill") {
                processTranscript()
            }
        }
    }

    private var statusPanel: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                ProgressView()
                    .controlSize(.small)
                    .opacity(isRunning ? 1 : 0)
                Text(statusTitle)
                    .font(.system(size: 13, weight: .semibold))
                Spacer()
            }

            ScrollView {
                Text(statusMessage)
                    .font(.system(size: 12, design: .monospaced))
                    .foregroundStyle(.secondary)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .textSelection(.enabled)
            }
            .frame(height: 92)
        }
        .padding(14)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(Color.white.opacity(0.34), lineWidth: 1)
                .allowsHitTesting(false)
        )
    }

    private func startLiveCall() {
        let selectedClientName = clientName
        let selectedSessionType = sessionType
        let shouldUseHeadphones = usesHeadphones

        runTask(title: "Starting live call", onSuccess: { output in
            if let id = parseSessionId(from: output) {
                sessionId = id
                UserDefaults.standard.set(id, forKey: "DiscoveryAgentLastSessionId")
                isRecording = true
                UserDefaults.standard.set(true, forKey: "DiscoveryAgentIsRecording")
                mode = .stop
                statusTitle = "Recording"
                statusMessage = "Recording started.\n\nSession ID:\n\(id)\n\nUse Stop to finalize transcription and generate the outputs."
            }
        }) {
            if shouldUseHeadphones {
                try switchToBlackHole()
            }

            return try runAction([
                "start",
                "--client-name", selectedClientName,
                "--session-type", selectedSessionType
            ])
        }
    }

    private func stopLiveCall() {
        let selectedSessionId = sessionId

        runTask(title: "Stopping live call", onSuccess: { _ in
            isRecording = false
            UserDefaults.standard.set(false, forKey: "DiscoveryAgentIsRecording")
            UserDefaults.standard.removeObject(forKey: "DiscoveryAgentLastSessionId")
            sessionId = ""
        }) {
            let output = try runAction(["stop", "--session-id", selectedSessionId])
            if UserDefaults.standard.string(forKey: "DiscoveryAgentOriginalInputDevice") != nil {
                _ = try? restoreOriginalInputDevice()
            }
            return output
        }
    }

    private func processTranscript() {
        let selectedTranscriptMode = transcriptMode
        let selectedTranscriptPath = transcriptPath
        let selectedTranscriptText = transcriptText

        runTask(title: "Processing transcript") {
            let path: String
            if selectedTranscriptMode == .file {
                guard !selectedTranscriptPath.isEmpty else { throw LauncherError.message("Choose a transcript file first.") }
                path = selectedTranscriptPath
            } else {
                let cleaned = selectedTranscriptText.trimmingCharacters(in: .whitespacesAndNewlines)
                guard !cleaned.isEmpty else { throw LauncherError.message("Paste a transcript first.") }
                let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("discovery-agent-transcript-\(UUID().uuidString).txt")
                try cleaned.write(to: tempURL, atomically: true, encoding: .utf8)
                path = tempURL.path
            }
            return try runAction(["test", "--transcript-path", path])
        }
    }

    private func chooseTranscriptFile() {
        let panel = NSOpenPanel()
        panel.title = "Choose Transcript"
        panel.canChooseFiles = true
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.allowedContentTypes = [.plainText, .text, .utf8PlainText]
        if panel.runModal() == .OK {
            transcriptPath = panel.url?.path ?? ""
        }
    }

    private func runTask(
        title: String,
        onSuccess: @escaping (String) -> Void = { _ in },
        work: @escaping () throws -> String
    ) {
        isRunning = true
        statusTitle = title
        if title == "Stopping live call" {
            statusMessage = "Stopping capture, draining the last audio chunk, transcribing, and generating outputs. This can take a few seconds."
        } else {
            statusMessage = "Working..."
        }

        let job = work
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let output = try job()
                DispatchQueue.main.async {
                    onSuccess(output)
                    isRunning = false
                    statusTitle = "Complete"
                    statusMessage = output
                }
            } catch {
                DispatchQueue.main.async {
                    isRunning = false
                    statusTitle = "Needs attention"
                    statusMessage = error.localizedDescription
                }
            }
        }
    }
}

private enum LauncherMode {
    case live
    case stop
    case transcript
}

private enum TranscriptMode {
    case file
    case paste
}

private enum LauncherError: LocalizedError {
    case message(String)

    var errorDescription: String? {
        switch self {
        case .message(let text):
            return text
        }
    }
}

private struct ModeButton: View {
    let title: String
    let systemImage: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 7) {
                Image(systemName: systemImage)
                    .font(.system(size: 19, weight: .semibold))
                Text(title)
                    .font(.system(size: 11, weight: .semibold))
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .frame(maxWidth: .infinity, minHeight: 70)
        }
        .buttonStyle(.plain)
        .foregroundStyle(isSelected ? .primary : .secondary)
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(isSelected ? Color.white.opacity(0.30) : Color.white.opacity(0.12))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(Color.white.opacity(isSelected ? 0.60 : 0.25), lineWidth: 1)
                .allowsHitTesting(false)
        )
        .shadow(color: .black.opacity(isSelected ? 0.18 : 0.06), radius: 12, y: 8)
    }
}

private struct PrimaryButton: View {
    let title: String
    let systemImage: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(title, systemImage: systemImage)
                .font(.system(size: 14, weight: .semibold))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(
            LinearGradient(
                colors: [Color.black.opacity(0.86), Color.black.opacity(0.68)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            ),
            in: RoundedRectangle(cornerRadius: 18, style: .continuous)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(Color.white.opacity(0.22), lineWidth: 1)
                .allowsHitTesting(false)
        )
        .shadow(color: .black.opacity(0.22), radius: 16, y: 10)
    }
}

private struct GlassPanel<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        content
            .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 34, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .stroke(
                        LinearGradient(
                            colors: [Color.white.opacity(0.85), Color.white.opacity(0.18), Color.white.opacity(0.45)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 1.2
                    )
                    .allowsHitTesting(false)
            )
            .overlay(alignment: .topLeading) {
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .fill(Color.white.opacity(0.16))
                    .blur(radius: 1)
                    .mask(
                        LinearGradient(colors: [.white, .clear], startPoint: .topLeading, endPoint: .center)
                    )
                    .allowsHitTesting(false)
            }
            .shadow(color: .black.opacity(0.24), radius: 28, y: 18)
    }
}

private struct VisualEffectView: NSViewRepresentable {
    let material: NSVisualEffectView.Material
    let blendingMode: NSVisualEffectView.BlendingMode

    func makeNSView(context: Context) -> NSVisualEffectView {
        let view = NSVisualEffectView()
        view.material = material
        view.blendingMode = blendingMode
        view.state = .active
        return view
    }

    func updateNSView(_ nsView: NSVisualEffectView, context: Context) {
        nsView.material = material
        nsView.blendingMode = blendingMode
        nsView.state = .active
    }
}

private struct WindowAccessor: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            guard let window = view.window else { return }
            window.isOpaque = false
            window.backgroundColor = .clear
            window.titlebarAppearsTransparent = true
            window.titleVisibility = .hidden
            window.isMovableByWindowBackground = true
            window.level = .floating
            window.center()
        }
        return view
    }

    func updateNSView(_ nsView: NSView, context: Context) {}
}

private func runAction(_ arguments: [String]) throws -> String {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: pythonPath)
    process.arguments = [actionScriptPath] + arguments
    process.currentDirectoryURL = URL(fileURLWithPath: projectDirectory)

    let pipe = Pipe()
    let errorPipe = Pipe()
    process.standardOutput = pipe
    process.standardError = errorPipe
    try process.run()
    process.waitUntilExit()

    let output = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    let errorOutput = String(data: errorPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    guard process.terminationStatus == 0 else {
        throw LauncherError.message(errorOutput.isEmpty ? output : errorOutput)
    }
    return output.trimmingCharacters(in: .whitespacesAndNewlines)
}

private func runShell(_ command: String) throws -> String {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/bin/zsh")
    process.arguments = ["-lc", command]
    let pipe = Pipe()
    let errorPipe = Pipe()
    process.standardOutput = pipe
    process.standardError = errorPipe
    try process.run()
    process.waitUntilExit()

    let output = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    let errorOutput = String(data: errorPipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
    guard process.terminationStatus == 0 else {
        throw LauncherError.message(errorOutput.isEmpty ? output : errorOutput)
    }
    return output.trimmingCharacters(in: .whitespacesAndNewlines)
}

private func switchToBlackHole() throws {
    let current = try runShell("SwitchAudioSource -t input -c")
    if !current.isEmpty {
        UserDefaults.standard.set(current, forKey: "DiscoveryAgentOriginalInputDevice")
    }
    let devices = try runShell("SwitchAudioSource -t input -a")
    if devices.components(separatedBy: .newlines).contains("BlackHole 2ch") {
        _ = try runShell("SwitchAudioSource -t input -s 'BlackHole 2ch'")
    } else if devices.components(separatedBy: .newlines).contains("BlackHole 16ch") {
        _ = try runShell("SwitchAudioSource -t input -u 'BlackHole16ch_UID'")
    } else {
        throw LauncherError.message("BlackHole is not available as an input device. Install BlackHole or choose 'Using headphones' off.")
    }
}

private func restoreOriginalInputDevice() throws -> String {
    guard let original = UserDefaults.standard.string(forKey: "DiscoveryAgentOriginalInputDevice"), !original.isEmpty else {
        return ""
    }
    let escaped = original.replacingOccurrences(of: "'", with: "'\\''")
    let output = try runShell("SwitchAudioSource -t input -s '\(escaped)'")
    UserDefaults.standard.removeObject(forKey: "DiscoveryAgentOriginalInputDevice")
    return output
}

private func parseSessionId(from output: String) -> String? {
    guard let data = output.data(using: .utf8),
          let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let id = json["session_id"] as? String else {
        return nil
    }
    return id
}
