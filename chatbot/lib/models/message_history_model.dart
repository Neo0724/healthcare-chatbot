enum MessageType { ai, human }

class MessageHistoryModel {
  final String _id;
  final MessageType _messageType;
  final String _content;
  final DateTime _createdAt;

  MessageHistoryModel({
    required this._id,
    required this._messageType,
    required this._content,
    required this._createdAt,
  });

  factory MessageHistoryModel.fromJson(Map<String, dynamic> json) {
    return MessageHistoryModel(
      id: json['_id'] as String,
      content: json['content'] as String,
      createdAt: DateTime.parse(json['createdAt']),
      messageType: MessageType.values.byName(json['type']),
    );
  }

  MessageHistoryModel copyWith({String? content}) {
    return MessageHistoryModel(
      id: id,
      messageType: messageType,
      content: content ?? this.content,
      createdAt: createdAt,
    );
  }

  String get id => _id;
  MessageType get messageType => _messageType;
  String get content => _content;
  DateTime get createdAt => _createdAt;
}
