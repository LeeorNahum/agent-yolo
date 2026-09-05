using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;

internal static class Launcher
{
    private static int Main()
    {
        bool hold = OwnsVisibleConsole();
        int code = 9009;
        try
        {
            if (!string.Equals(Path.GetFileNameWithoutExtension(typeof(Launcher).Assembly.Location), Wrapper.Name, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Keep the original launcher filename to prevent CLI resolution recursion.");
            string cwd = Directory.GetCurrentDirectory();
            string executable = FindExecutable(Wrapper.Command);
            if (executable == null)
                throw new FileNotFoundException(Wrapper.Command + ".exe was not found on an absolute PATH entry. Install the native CLI. Batch-only installations cannot preserve arbitrary Windows arguments or UNC working directories.");

            // Forward the Windows command line without parsing or shell evaluation.
            var start = new ProcessStartInfo(executable, Wrapper.Permission + RawArguments());
            start.UseShellExecute = false;
            start.WorkingDirectory = cwd;
            Console.CancelKeyPress += delegate(object sender, ConsoleCancelEventArgs e) { e.Cancel = true; };
            using (Process child = Process.Start(start))
            {
                child.WaitForExit();
                code = child.ExitCode;
            }
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(Wrapper.Name + ": " + error.Message);
        }
        if (hold)
        {
            Console.WriteLine("Agent exited. Press any key to close this window.");
            try { Console.ReadKey(true); }
            catch (InvalidOperationException) { }
        }
        return code;
    }

    private static string RawArguments()
    {
        string line = Environment.CommandLine;
        int i = 0;
        while (i < line.Length && (line[i] == ' ' || line[i] == '\t')) i++;
        bool quoted = false;
        while (i < line.Length)
        {
            if (line[i] == '"') quoted = !quoted;
            else if (!quoted && (line[i] == ' ' || line[i] == '\t')) break;
            i++;
        }
        return line.Substring(i);
    }

    private static string FindExecutable(string command)
    {
        string self = Path.GetFullPath(typeof(Launcher).Assembly.Location);
        foreach (string entry in (Environment.GetEnvironmentVariable("PATH") ?? "").Split(';'))
        {
            string dir = entry.Trim().Trim('"');
            // IsPathRooted also accepts C:relative and \relative, which are not absolute.
            if (!(dir.StartsWith(@"\\") || (dir.Length >= 3 && char.IsLetter(dir[0]) && dir[1] == ':' && (dir[2] == '\\' || dir[2] == '/')))) continue;
            try
            {
                string candidate = Path.GetFullPath(Path.Combine(dir, command + ".exe"));
                if (!string.Equals(candidate, self, StringComparison.OrdinalIgnoreCase) && File.Exists(candidate)) return candidate;
            }
            catch (ArgumentException) { }
            catch (NotSupportedException) { }
            catch (PathTooLongException) { }
        }
        return null;
    }

    [DllImport("kernel32.dll")]
    private static extern uint GetConsoleProcessList(uint[] processes, uint count);
    [DllImport("kernel32.dll")]
    private static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr window);

    private static bool OwnsVisibleConsole()
    {
        try
        {
            return !Console.IsInputRedirected && GetConsoleProcessList(new uint[2], 2) == 1 && IsWindowVisible(GetConsoleWindow());
        }
        catch { return false; }
    }
}
