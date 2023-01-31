
 import platform

# class test:
#     def os_type():
#         os_system = platform.system()
#         return os_system

#     # print(os_type().os_system())
#     # def printing_os_type():
#     #     if os_type() == 'Darwin':
#     #         pass
#     def print_os_type(os_system):
#         if os_system == 'Darwin':
#             print("SS")
#         # print(os_type())


#     # if os_type() == 'Darwin':
#     #     print("DD")

# # print(os_type())

# # print(platform.system())
computer_name = platform.node().split(".")

print(computer_name[0])
print(type(computer_name))