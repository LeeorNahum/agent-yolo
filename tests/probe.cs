using System;
using System.IO;
using System.Text;

internal static class Probe
{
    private static int Main(string[] args)
    {
        using (var output = new StreamWriter(Environment.GetEnvironmentVariable("AGENT_YOLO_CAPTURE"), false, Encoding.ASCII))
        {
            output.WriteLine(Convert.ToBase64String(Encoding.Unicode.GetBytes(Directory.GetCurrentDirectory())));
            output.WriteLine(Convert.ToBase64String(Encoding.Unicode.GetBytes(Environment.CommandLine)));
            foreach (string arg in args) output.WriteLine(Convert.ToBase64String(Encoding.Unicode.GetBytes(arg)));
        }
        return 37;
    }
}
