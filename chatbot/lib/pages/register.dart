import 'package:chatbot/utils/custom_dio.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class Register extends StatefulWidget {
  const Register({super.key});

  @override
  State<Register> createState() => _RegisterState();
}

class _RegisterState extends State<Register> {
  bool _isPasswordVisible = false;
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  String _errorMessage = "";
  String _errorUsername = "";
  String _errorPassword = "";
  bool _registerSuccess = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  bool _validateInput(String username, String password) {
    bool isValid = true;

    if (username.isEmpty) {
      setState(() {
        _errorUsername = "Username cannot be empty";
      });
      isValid = false;
    }

    if (username.length > 20) {
      setState(() {
        _errorUsername = "Username cannot be more than 20 characters";
      });
      isValid = false;
    }

    if (password.isEmpty || password.length < 6) {
      setState(() {
        _errorPassword = "Password must have at least 6 characters";
      });
      isValid = false;
    }

    if (password.length > 20) {
      setState(() {
        _errorPassword = "Password cannot be more than 20 characters";
      });
      isValid = false;
    }

    return isValid;
  }

  Future<void> handleRegister(String username, String password) async {
    setState(() {
      _errorMessage = "";
      _errorPassword = "";
      _errorUsername = "";
    });

    if (!_validateInput(username, password)) {
      return;
    }

    try {
      final response = await CustomDio.getCustomDio().post(
        "/auth/register",
        data: {"username": username, "password": password},
      );

      if (response.statusCode == 201 && response.data["success"]) {
        setState(() {
          _registerSuccess = true;
        });
        return;
      }
    } on DioException catch (e) {
      if (e.response != null) {
        final statusCode = e.response!.statusCode;
        final data = e.response!.data;

        if (statusCode == 400) {
          setState(() {
            _errorMessage = data["error"];
          });
        }
      } else {
        // No response received (timeout, connection error, etc.)
        debugPrint("Dio error: ${e.message}");
        setState(() {
          _errorMessage = "Network error";
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212), // Global dark gray background
      appBar: AppBar(
        title: const Text("Register"),
        elevation: 0,
        centerTitle: true,
        backgroundColor: const Color(0xFF1E1E1E),
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16.0),
              ),
              color: const Color(0xFF1E1E1E), // Card dark background
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      "Create Account",
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 24,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      "Register Now to get started",
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                    const SizedBox(height: 32),
                    _usernameInput(),
                    const SizedBox(height: 16),
                    _passwordInput(),
                    const SizedBox(height: 24),
                    _submitBtn(),
                    if (_errorMessage.isNotEmpty) ...[
                      const SizedBox(height: 16),
                      Text(
                        _errorMessage,
                        style: const TextStyle(
                          color: Colors.redAccent,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                    if (_registerSuccess) ...[
                      const SizedBox(height: 16),
                      const Text(
                        "Register Successful! You may login now.",
                        style: TextStyle(
                          color: Colors.greenAccent,
                          fontWeight: FontWeight.w600,
                          fontSize: 14,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Already have an account?",
                          style: TextStyle(color: Colors.grey),
                        ),
                        const SizedBox(width: 4),
                        GestureDetector(
                          onTap: () {
                            context.go('/login');
                          },
                          child: Text(
                            "Login now",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.blueAccent,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  GestureDetector _submitBtn() {
    return GestureDetector(
      onTap: () {
        final username = _usernameController.text;
        final password = _passwordController.text;
        handleRegister(username, password);
      },
      child: Container(
        height: 48,
        decoration: BoxDecoration(
          color: Colors.white, // Crisp white stands out sharply in dark mode
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Center(
          child: Text(
            "Register",
            style: TextStyle(
              color: Color(0xFF121212), // Dark text for contrast
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ),
      ),
    );
  }

  Column _usernameInput() {
    return Column(
      children: [
        const Align(
          alignment: Alignment.centerLeft,
          child: Text(
            "Username:",
            textAlign: TextAlign.start,
            style: TextStyle(
              color: Colors.white70, // Matches dark mode text hierarchy
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        const SizedBox(height: 10),
        TextField(
          controller: _usernameController,
          style: const TextStyle(color: Colors.white),
          onChanged: (value) => setState(() {
            _errorUsername = "";
          }),
          decoration: InputDecoration(
            filled: true,
            fillColor: const Color(0xFF2C2C2C),
            contentPadding: const EdgeInsets.all(14),
            labelText: "Enter Username",
            labelStyle: const TextStyle(color: Colors.grey, fontSize: 14),

            // Enabled Border
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorUsername.isNotEmpty
                    ? Colors.redAccent
                    : Colors.transparent, // Subtle border for dark mode
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(8),
            ),

            // Focused Border
            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorUsername.isNotEmpty
                    ? Colors.redAccent
                    : Colors.white,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(8),
            ),

            errorMaxLines: 3,
            errorText: _errorUsername.isNotEmpty ? _errorUsername : null,
            errorStyle: const TextStyle(color: Colors.redAccent),
          ),
        ),
      ],
    );
  }

  Column _passwordInput() {
    return Column(
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: Text(
            "Password:",
            textAlign: TextAlign.start,
            style: TextStyle(
              color: Colors.white70, // Matches dark mode text hierarchy
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        SizedBox(height: 10),
        TextField(
          controller: _passwordController,
          onChanged: (value) => setState(() {
            _errorPassword = "";
          }),
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            filled: true,
            fillColor: const Color(0xFF2C2C2C),
            contentPadding: EdgeInsets.all(10),
            labelText: "Enter Password",
            labelStyle: TextStyle(color: Colors.grey, fontSize: 14),
            suffixIcon: IconButton(
              onPressed: () {
                setState(() {
                  _isPasswordVisible = !_isPasswordVisible;
                });
              },
              icon: Icon(
                _isPasswordVisible ? Icons.visibility_off : Icons.visibility,
                color: Colors.white,
              ),
              iconSize: 14,
            ),

            // Show red border if error exists
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorPassword.isNotEmpty
                    ? Colors.red
                    : Colors.transparent,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(8),
            ),

            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorPassword.isNotEmpty ? Colors.red : Colors.white,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(8),
            ),

            errorMaxLines: 3,
            errorText: _errorPassword.isNotEmpty ? _errorPassword : null,
            errorStyle: const TextStyle(color: Colors.redAccent),
          ),
          obscureText: !_isPasswordVisible,
          keyboardType: TextInputType.visiblePassword,
        ),
      ],
    );
  }
}
