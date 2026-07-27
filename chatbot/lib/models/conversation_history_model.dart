class ConversationHistoryModel {
  final String _id;
  final DateTime _createdAt;
  final String _title;

  ConversationHistoryModel({
    required this._id,
    required this._createdAt,
    required this._title,
  });

  factory ConversationHistoryModel.fromJson(Map<String, dynamic> json) {
    return ConversationHistoryModel(
      id: json['_id'] as String,
      title: json['title'] as String,
      createdAt: DateTime.parse(json['createdAt']),
    );
  }

  String get id => _id;
  DateTime get createdAt => _createdAt;
  String get title => _title;
}
