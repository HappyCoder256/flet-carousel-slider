// import 'package:flet/flet.dart';


// CreateControlFactory createControl = (CreateControlArgs args) {
//   switch (args.control.type) {
//     case "flet_carousel_slider":
//       return FletCarouselSliderControl(
//         parent: args.parent,
//         control: args.control,
//       );
//     default:
//       return null;
//   }
// };




// library flet_carousel;

import 'package:flet/flet.dart';
import 'flet_carousel_slider.dart';

// import 'src/carousel.dart';

/// Called by Flet's plugin loader to register custom controls.
CreateControlFactory createControl = (CreateControlArgs args) {
  switch (args.control.type) {
    case "flet_carousel_slider":
      return FletCarouselSliderControl(
        parent: args.parent,
        control: args.control,
        children: args.children,
        backend: args.backend,
      );
    default:
      return null;
  }
};

void ensureInitialized() {
  // nothing to initialize
}