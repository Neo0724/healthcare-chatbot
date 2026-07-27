import 'package:chatbot/router/app_router.dart';
import 'package:chatbot/states/auth_state.dart';
import 'package:chatbot/utils/custom_dio.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:go_router/go_router.dart';

class Login extends StatefulWidget {
  const Login({super.key});

  @override
  State<Login> createState() => _LoginState();
}

class _LoginState extends State<Login> {
  bool _isPasswordVisible = false;
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  String _errorMessage = "";
  String _errorUsername = "";
  String _errorPassword = "";
  final storage = FlutterSecureStorage();

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

  Future<void> handleLogin(String username, String password) async {
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
        "/auth/login",
        data: {"username": username, "password": password},
      );

      if (response.statusCode == 200 && response.data["success"]) {
        final String accessToken = response.data["access_token"];
        final String refreshToken = response.data["refresh_token"];

        await storage.write(key: "access_token", value: accessToken);
        await storage.write(key: "refresh_token", value: refreshToken);
        await storage.write(key: "username", value: username);

        AuthState.login();
        appRouter.go("/");
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
        } else if (statusCode == 401) {
          setState(() {
            _errorMessage = "Invalid username or password";
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
      appBar: AppBar(title: Text("Login")),
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
                      "Login Now",
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
                  SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text("Do not have an account?"),
                      SizedBox(width: 5),
                      GestureDetector(
                        onTap: () {
                          context.go('/register');
                        },
                        child: Text(
                          "Register now",
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
        handleLogin(username, password);
      },
      child: Container(
        height: 40,
        decoration: BoxDecoration(
          color: Colors.lightBlue,
          borderRadius: BorderRadius.circular(7),
        ),
        child: Center(
          child: Text(
            "Login",
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
            suffixIcon: IconButton(
              onPressed: () {
                setState(() {
                  _isPasswordVisible = !_isPasswordVisible;
                });
              },
              icon: Icon(
                _isPasswordVisible ? Icons.visibility_off : Icons.visibility,
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
