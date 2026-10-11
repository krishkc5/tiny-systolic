# Read-only reporting hook: never changes clocks, exceptions or constraints.
# The flow's generic worst-path-per-endpoint report can select only input paths;
# explicitly restrict launch/capture pins to inspect internal sequential paths.
set audit_launch [all_registers -output_pins]
set audit_capture [all_registers -data_pins]
puts "%OL_CREATE_REPORT register_paths.rpt"
puts "Explicit register-to-register audit: $corner_name"
puts "Launch pins: [llength $audit_launch]; capture pins: [llength $audit_capture]"
foreach audit_delay {max min} {
    puts "Register-to-register $audit_delay paths"
    report_checks -from $audit_launch -to $audit_capture -path_delay $audit_delay \
        -sort_by_slack -group_path_count 1000 -corner $corner_name \
        -fields {slew cap input net fanout} -format full_clock_expanded
}
puts "%OL_END_REPORT"
