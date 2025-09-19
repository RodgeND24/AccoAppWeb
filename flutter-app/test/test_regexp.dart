
void main() {
final emailRegExp = RegExp(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)');
const String email = 'dimamail.ru';

final isMatch = emailRegExp.hasMatch(email);
print(isMatch);
}

