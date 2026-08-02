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
              title: const Text("Change Username"),
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
                    errorText: errorMessage.isNotEmpty ? errorMessage : null,
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.grey),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.blue),
                    ),
                    errorBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.red),
                    ),
                    focusedErrorBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: Colors.red),
                    ),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("Cancel"),
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
                          const SnackBar(
                            content: Text("Username updated successfully"),
                            backgroundColor: Colors.green,
                            duration: Duration(seconds: 2),
                            behavior: SnackBarBehavior.floating,
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
                  child: const Text("Save"),
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
              title: const Text("Change Password"),
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
                          errorText: currentPasswordError.isNotEmpty
                              ? currentPasswordError
                              : null,
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.grey),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.blue),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.red),
                          ),
                          focusedErrorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.red),
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
                          labelText: "New Password",
                          errorText: newPasswordError.isNotEmpty
                              ? newPasswordError
                              : null,
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.grey),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.blue),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.red),
                          ),
                          focusedErrorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.red),
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
                          errorText: confirmPasswordError.isNotEmpty
                              ? confirmPasswordError
                              : null,
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.grey),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.blue),
                          ),
                          errorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.red),
                          ),
                          focusedErrorBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: const BorderSide(color: Colors.red),
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
                  child: const Text("Cancel"),
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
                          const SnackBar(
                            content: Text("Password updated successfully"),
                            backgroundColor: Colors.green,
                            duration: Duration(seconds: 2),
                            behavior: SnackBarBehavior.floating,
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
                  child: const Text("Save"),
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
      ),
      body: Center(
        child: SizedBox(
          width: 500,
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                const CircleAvatar(
                  radius: 45,
                  child: Icon(Icons.person, size: 50),
                ),

                const SizedBox(height: 40),

                Card(
                  child: ListTile(
                    leading: const Icon(Icons.person_outline),
                    title: const Text("Username"),
                    subtitle: Text(_username),
                    trailing: IconButton(
                      icon: const Icon(Icons.edit),
                      onPressed: () => _showUsernameDialog(context),
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                Card(
                  child: ListTile(
                    leading: const Icon(Icons.lock_outline),
                    title: const Text("Password"),
                    subtitle: const Text("••••••••"),
                    trailing: IconButton(
                      icon: const Icon(Icons.edit),
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
