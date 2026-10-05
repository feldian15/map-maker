# Keep V1 CLI Thin and Route Engine Reusable

V1 will ship as a command-line tool only, but route generation must live behind reusable Python application interfaces rather than inside CLI argument handling. This keeps the MVP focused on proving route geometry against real travel networks while allowing a future dedicated UI to call the same route engine without a rewrite.
