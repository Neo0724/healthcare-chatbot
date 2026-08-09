import 'package:chatbot/utils/custom_dio.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class Profile extends StatefulWidget {
  const Profile({super.key});

  @override
  State<Profile> createState() => _ProfileState();
}

class _ProfileState extends State<Profile> {
  final storage = FlutterSecureStorage();
  String _username = "";

  Future<void> _loadUsername() async {
    final username = await storage.read(key: 'username');

    if (username != null) {
      setState(() {
        _username = username;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _loadUsername();
  }

  void _showUsernameDialog(BuildContext context) {
    final controller = TextEditingController();

    showDialog(
      context: context,
      builder: (_) {
        String errorMessage = "";

        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              backgroundColor: const Color(0xFF121212),
              title: const Text(
                "Change Username",
                style: TextStyle(color: Colors.white),
              ),
              content: SizedBox(
                width: 350,
                child: TextField(
                  controller: controller,
                  onChanged: (_) {
                    setDialogState(() {
                      errorMessage = "";
                    });
                  },
                  decoration: InputDecoration(
                    labelText: "New Username",
                    labelStyle: const TextStyle(color: Colors.white70),
                    filled: true,
                    fillColor: const Color(0xFF2C2C2C), //
                    errorText: errorMessage.isNotEmpty ? errorMessage : null,
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide(color: Colors.grey[700]!),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.white),
                    ),
                    errorBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.redAccent),
                    ),
                    focusedErrorBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.redAccent),
                    ),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  style: ButtonStyle(
                    backgroundColor: WidgetStatePropertyAll(Color(0xFF2C2C2C)),
                  ),
                  child: const Text(
                    "Cancel",
                    style: TextStyle(color: Colors.white),
                  ),
                ),
                FilledButton(
                  onPressed: () async {
                    // Update username
                    final String newUsername = controller.text;

                    if (newUsername.isEmpty) {
                      setDialogState(() {
                        errorMessage = "At least 1 character is required";
                      });
                      return;
                    } else if (newUsername.length > 20) {
                      setDialogState(() {
                        errorMessage = "Only up-to 20 characters are allowed";
                      });
                      return;
                    }

                    try {
                      final response = await CustomDio.getCustomDio().post(
                        '/update-username',
                        data: {"username": newUsername},
                      );

                      if (!context.mounted) return;

                      if (response.statusCode == 200 &&
                          response.data["success"]) {
                        Navigator.pop(context);
                        storage.write(key: 'username', value: newUsername);
                        setState(() {
                          _username = newUsername;
                        });
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: const Text(
                              "Username updated successfully",
                            ),
                            backgroundColor: Colors.green,
                            duration: const Duration(seconds: 2),
                            behavior: SnackBarBehavior.floating,
                            width: 500,
                            shape: RoundedRectangleBorder(
                              borderRadius: .circular(10.0),
                            ),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 15.0,
                              vertical: 10.0,
                            ),
                            action: SnackBarAction(
                              label: 'OK',
                              onPressed: () {},
                            ),
                          ),
                        );
                        return;
                      }

                      final String? errorMsg = (response.data["error"]);

                      if (errorMsg != null) {
                        setDialogState(() {
                          errorMessage = errorMsg;
                        });
                      }
                    } on DioException catch (err) {
                      setDialogState(() {
                        errorMessage =
                            err.response?.data["error"]?.toString() ??
                            err.toString();
                      });
                    }
                  },
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.all(Colors.white),
                  ),
                  child: const Text(
                    "Save",
                    style: TextStyle(
                      color: Colors.black,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  void _showPasswordDialog(BuildContext context) {
    final currentController = TextEditingController();
    final newController = TextEditingController();
    final confirmController = TextEditingController();

    showDialog(
      context: context,
      builder: (_) {
        String currentPasswordError = "";
        String newPasswordError = "";
        String confirmPasswordError = "";

        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              backgroundColor: const Color(0xFF121212),
              title: const Text(
                "Change Password",
                style: TextStyle(color: Colors.white),
              ),
              content: SingleChildScrollView(
                child: SizedBox(
                  width: 350,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextField(
                        controller: currentController,
                        obscureText: true,
                        onChanged: (_) {
                          setDialogState(() {
                            currentPasswordError = "";
                          });
                        },
                        decoration: InputDecoration(
                          labelText: "Current Password",
                          labelStyle: const TextStyle(color: Colors.white70),
                          filled: true,
                          fillColor: const Color(0xFF2C2C2C), //
                          errorText: currentPasswordError.isNotEmpty
                              ? currentPasswordError
                              : null,
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide(color: Colors.grey[700]!),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.white),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(
                              color: Colors.redAccent,
                            ),
                          ),
                          focusedErrorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(
                              color: Colors.redAccent,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: newController,
                        obscureText: true,
                        onChanged: (_) {
                          setDialogState(() {
                            newPasswordError = "";
                          });
                        },
                        decoration: InputDecoration(
                          filled: true,
                          fillColor: const Color(0xFF2C2C2C), //
                          labelText: "New Password",
                          labelStyle: const TextStyle(color: Colors.white70),
                          errorText: newPasswordError.isNotEmpty
                              ? newPasswordError
                              : null,
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide(color: Colors.grey[700]!),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.white),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(
                              color: Colors.redAccent,
                            ),
                          ),
                          focusedErrorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(
                              color: Colors.redAccent,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextField(
                        controller: confirmController,
                        obscureText: true,
                        onChanged: (_) {
                          setDialogState(() {
                            confirmPasswordError = "";
                          });
                        },
                        decoration: InputDecoration(
                          labelText: "Confirm Password",
                          labelStyle: const TextStyle(color: Colors.white70),
                          filled: true,
                          fillColor: const Color(
                            0xFF2C2C2C,
                          ), // Matches your dark input field background
                          contentPadding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 14,
                          ),
                          errorText: confirmPasswordError.isNotEmpty
                              ? confirmPasswordError
                              : null,
                          errorStyle: const TextStyle(color: Colors.redAccent),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide(color: Colors.grey[700]!),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.white),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(
                              color: Colors.redAccent,
                            ),
                          ),
                          focusedErrorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(
                              color: Colors.redAccent,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  style: ButtonStyle(
                    backgroundColor: WidgetStatePropertyAll(Color(0xFF2C2C2C)),
                  ),
                  child: const Text(
                    "Cancel",
                    style: TextStyle(color: Colors.white),
                  ),
                ),
                FilledButton(
                  onPressed: () async {
                    String currentPassword = currentController.text;
                    String newPassword = newController.text;
                    String confirmPassword = confirmController.text;
                    bool isValid = true;

                    if (currentPassword.length < 6) {
                      setDialogState(() {
                        currentPasswordError =
                            "At least 6 characters are required";
                      });
                      isValid = false;
                    }

                    if (newPassword.length < 6) {
                      setDialogState(() {
                        newPasswordError = "At least 6 characters are required";
                      });
                      isValid = false;
                    }

                    if (confirmPassword.length < 6) {
                      setDialogState(() {
                        confirmPasswordError =
                            "At least 6 characters are required";
                      });
                      isValid = false;
                    }

                    if (currentPassword.length > 20) {
                      setDialogState(() {
                        currentPasswordError =
                            "Only up-to 20 characters are allowed";
                      });
                      isValid = false;
                    }

                    if (newPassword.length > 20) {
                      setDialogState(() {
                        newPasswordError =
                            "Only up-to 20 characters are allowed";
                      });
                      isValid = false;
                    }

                    if (confirmPassword.length > 20) {
                      setDialogState(() {
                        confirmPasswordError =
                            "Only up-to 20 characters are allowed";
                      });
                      isValid = false;
                    }

                    if (confirmPassword != newPassword) {
                      setDialogState(() {
                        confirmPasswordError = "Password not matched";
                      });
                      confirmController.text = "";
                      isValid = false;
                    }

                    if (!isValid) return;

                    try {
                      final response = await CustomDio.getCustomDio().post(
                        '/update-password',
                        data: {
                          "current_password": currentPassword,
                          "new_password": newPassword,
                        },
                      );

                      if (!context.mounted) return;

                      if (response.statusCode == 200 &&
                          response.data["success"]) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: const Text(
                              "Password updated successfully",
                            ),
                            backgroundColor: Colors.green,
                            duration: const Duration(seconds: 2),
                            behavior: SnackBarBehavior.floating,
                            width: 500,
                            shape: RoundedRectangleBorder(
                              borderRadius: .circular(10.0),
                            ),
                            padding: const EdgeInsets.symmetric(
                              horizontal: 15.0,
                              vertical: 10.0,
                            ),
                            action: SnackBarAction(
                              label: 'OK',
                              onPressed: () {},
                            ),
                          ),
                        );
                        Navigator.pop(context);
                        return;
                      }
                    } on DioException catch (err) {
                      dynamic data = err.response?.data;

                      if (data["error"] is Map<String, String>) {
                        Map<String, dynamic> error = data["error"];

                        if (error.containsKey("current_password")) {
                          setDialogState(() {
                            currentPasswordError = error["current_password"];
                          });
                        } else if (error.containsKey("new_password")) {
                          setDialogState(() {
                            newPasswordError = error["new_password"];
                          });
                        }
                      } else if (data["error"] is String) {
                        // if "error" is just a string
                        setDialogState(() {
                          currentPasswordError = data["error"];
                        });
                      }
                    }
                  },
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.all(Colors.white),
                  ),
                  child: const Text(
                    "Save",
                    style: TextStyle(
                      color: Colors.black,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Profile",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        elevation: 0,
        centerTitle: true,
        backgroundColor: const Color(0xFF1E1E1E),
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 45,
                  backgroundColor: const Color(0xFF1E1E1E),
                  child: const Icon(
                    Icons.person,
                    size: 50,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 40),
                Card(
                  elevation: 4,
                  color: const Color(0xFF1E1E1E), // Dark card background
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: ListTile(
                    leading: const Icon(
                      Icons.person_outline,
                      color: Colors.white70,
                    ),
                    title: const Text(
                      "Username",
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    subtitle: Text(
                      _username,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    trailing: IconButton(
                      icon: const Icon(Icons.edit, color: Colors.white),
                      onPressed: () => _showUsernameDialog(context),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Card(
                  elevation: 4,
                  color: const Color(0xFF1E1E1E), // Dark card background
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: ListTile(
                    leading: const Icon(
                      Icons.lock_outline,
                      color: Colors.white70,
                    ),
                    title: const Text(
                      "Password",
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                    subtitle: const Text(
                      "••••••••",
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    trailing: IconButton(
                      icon: const Icon(Icons.edit, color: Colors.white),
                      onPressed: () => _showPasswordDialog(context),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
