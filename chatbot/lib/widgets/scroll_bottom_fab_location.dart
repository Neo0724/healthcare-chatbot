import 'package:flutter/material.dart';

class ScrollBottomFabLocation extends FloatingActionButtonLocation {
  ScrollBottomFabLocation();

  @override
  Offset getOffset(ScaffoldPrelayoutGeometry scaffoldGeometry) {
    // Get total screen dimensions from scaffold geometry
    final double x = scaffoldGeometry.scaffoldSize.width - 75;
    final double y = scaffoldGeometry.scaffoldSize.height - 150;
    return Offset(x, y);
  }
}
