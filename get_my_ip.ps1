# This script finds the property "Lease Obtained" in the 'ipconfig /all' console
# output and gets the 5 lines ABOVE the match. The IPv4 Address should be in one
# of the 5 lines above that property.
# Then it's a simple match to find the IPv4 Address (there should only be one)
# and write it to a file.

# Usage:
# echo Get IP Address
# Powershell.exe -executionpolicy remotesigned -File get-my-ip.ps1
# FOR /F %%i in ('type tmp_ip.txt') do set "my_ip=%%i"
# echo my_ip: %my_ip%
# del tmp_ip.txt

$textfile = "tmp_ip.txt"
ipconfig /all | Select-String -Pattern "Lease Obtained" -Context 5,0 | Out-File $textfile
# Alternate way to get IPv4 but uses hard coded network adapter type (i.e. "Wi-Fi", "ethernet", etc.)
#Get-NetIPAddress -AddressState Preferred -AddressFamily IPv4 -InterfaceAlias "Wi-Fi"
$iplist = Get-Content $textfile
$regex = '[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*'
$iplist | Select-String -Pattern IPv4 | Out-File $textfile
$iplist = Get-Content $textfile
$iplist | Select-String -Pattern $regex | %{$_.matches} | % { $_.value } | Out-File $textfile
