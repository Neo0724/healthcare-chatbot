import 'package:chatbot/utils/custom_dio.dart';
import 'package:flutter/material.dart';
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
  String errorMessage = "";

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> handleLogin(String username, String password) async {
    errorMessage = "";

    try {
      final response = await CustomDio.getCustomDio().post(
        "/auth/login",
        data: {"username": username, "password": password},
      );

      if (response.statusCode == 200 && response.data["success"]) {
        debugPrint(response.data.toString());
        return;
      }

      if (response.statusCode == 400) {
        errorMessage = response.data["error"][0]["msg"];
        debugPrint(response.data.toString());
        return;
      }

      errorMessage = response.data["error"];
      debugPrint(response.data.toString());
    } catch (e) {
      debugPrint(e.toString());
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
                  SizedBox(height: 10),
                  if (errorMessage.isNotEmpty)
                    Text(
                      errorMessage,
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight(800),
                      ),
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
          decoration: InputDecoration(
            filled: true,
            fillColor: Colors.white,
            contentPadding: EdgeInsets.all(10),
            hintText: "Enter Username",
            hintStyle: TextStyle(color: Color(0xffDDDADA), fontSize: 14),
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
          ),
          obscureText: !_isPasswordVisible,
          keyboardType: TextInputType.visiblePassword,
        ),
      ],
    );
  }
}
