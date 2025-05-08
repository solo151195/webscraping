# from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
#
# # Initialize VPN with country selection
# vpn_settings = initialize_VPN(area_input=['Netherlands'])
#
# # Rotate to the selected country
# rotate_VPN(vpn_settings)
#
# # Your code using the VPN goes here...
#
# # Terminate the VPN connection
# terminate_VPN(vpn_settings)
area_input=['Netherlands']
settings_servers = [area.lower() for area in area_input]
settings_servers = ",".join(settings_servers)
print(settings_servers)
# import subprocess
#
# with open("nordvpn/countrylist.txt", "r") as file:
#     areas_list = file.readlines()
# areas_list = [area.strip() for area in areas_list]
# # print(areas_list)
# country_dict = {'countries':areas_list[0:60],'europe': areas_list[0:36], 'americas': areas_list[36:44],
#                 'africa east india': areas_list[49:60],'asia pacific': areas_list[49:60],
#                 'regions australia': areas_list[60:65],'regions canada': areas_list[65:68],
#                 'regions germany': areas_list[68:70], 'regions india': areas_list[70:72],
#                 'regions united states': areas_list[72:87],'special groups':areas_list[87:len(areas_list)]}
#
# def connect_vpn(country):
#     try:
#         result = subprocess.run(["nordvpn", "-c", "-g", country], capture_output=True, text=True, check=True)
#         print("Connected to", country)
#         print(result.stdout)
#     except subprocess.CalledProcessError as e:
#         print("Connection failed:")
#         print(e.stderr)
#
# def disconnect_vpn():
#     try:
#         result = subprocess.run(["nordvpn", "-d"], capture_output=True, text=True, check=True)
#         print("Disconnected")
#     except subprocess.CalledProcessError as e:
#         print("Disconnection failed:")
#         print(e.stderr)
#
# # Example
# connect_vpn("Netherlands")
# # Later...
# # disconnect_vpn()
