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
            _errorMessage = data["error"][0]["msg"];
          });
        } else {
          setState(() {
            _errorMessage = data["error"] ?? "Something went wrong";
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
      appBar: AppBar(title: Text("Register")),
      body: Center(
        child: Container(
          height: 450,
          width: 350,
          margin: EdgeInsets.all(10),
          padding: EdgeInsets.all(20),
          decoration: BoxDecoration(
            shape: BoxShape.rectangle,
            borderRadius: BorderRadius.circular(7.0),
            border: BoxBorder.all(color: Colors.red, width: 3),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Text(
                      "Register Now",
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                      ),
                    ),
                  ),
                  SizedBox(height: 30),
                  _usernameInput(),
                  SizedBox(height: 30),
                  _passwordInput(),
                  SizedBox(height: 30),
                  _submitBtn(),
                  SizedBox(height: 15),
                  if (_errorMessage.isNotEmpty)
                    Text(
                      _errorMessage,
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight(800),
                      ),
                      textAlign: TextAlign.center,
                    ),
                  if (_registerSuccess)
                    Text(
                      "Register Successfull! You may login now.",
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight(800),
                      ),
                      textAlign: TextAlign.center,
                    ),
                  SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text("Already have an account?"),
                      SizedBox(width: 5),
                      GestureDetector(
                        onTap: () {
                          context.go('/login');
                        },
                        child: Text(
                          "Login now",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
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
        height: 40,
        decoration: BoxDecoration(
          color: Colors.lightBlue,
          borderRadius: BorderRadius.circular(7),
        ),
        child: Center(
          child: Text(
            "Register",
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  Column _usernameInput() {
    return Column(
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: Text("Username:", textAlign: TextAlign.start),
        ),
        SizedBox(height: 10),
        TextField(
          controller: _usernameController,
          onChanged: (value) => setState(() {
            _errorUsername = "";
          }),
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.white,
            contentPadding: EdgeInsets.all(10),
            hintText: "Enter Username",
            hintStyle: TextStyle(color: Color(0xffDDDADA), fontSize: 14),
            // Show red border if error exists
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorUsername.isNotEmpty
                    ? Colors.red
                    : Colors.transparent,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(5),
            ),

            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorUsername.isNotEmpty ? Colors.red : Colors.blue,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(5),
            ),

            errorText: _errorUsername.isNotEmpty ? _errorUsername : null,
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
          child: Text("Password:", textAlign: TextAlign.start),
        ),
        SizedBox(height: 10),
        TextField(
          controller: _passwordController,
          onChanged: (value) => setState(() {
            _errorPassword = "";
          }),
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.white,
            contentPadding: EdgeInsets.all(10),
            hintText: "Enter Password",
            hintStyle: TextStyle(color: Color(0xffDDDADA), fontSize: 14),
            suffix: GestureDetector(
              child: Text("Visible"),
              onTap: () {
                setState(() {
                  _isPasswordVisible = !_isPasswordVisible;
                });
              },
            ),
            // Show red border if error exists
            enabledBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorPassword.isNotEmpty
                    ? Colors.red
                    : Colors.transparent,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(5),
            ),

            focusedBorder: OutlineInputBorder(
              borderSide: BorderSide(
                color: _errorPassword.isNotEmpty ? Colors.red : Colors.blue,
                width: 1.5,
              ),
              borderRadius: BorderRadius.circular(5),
            ),

            errorText: _errorPassword.isNotEmpty ? _errorPassword : null,
          ),
          obscureText: !_isPasswordVisible,
          keyboardType: TextInputType.visiblePassword,
        ),
      ],
    );
  }
}
