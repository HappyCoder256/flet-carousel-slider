import 'package:carousel_slider_plus/carousel_slider_plus.dart';
import 'package:flet/flet.dart';
import 'package:flutter/material.dart';

class FletCarouselSliderControl extends StatefulWidget {
  final Control? parent;
  final Control control;
  final List<Control> children;
  final FletControlBackend backend;

  const FletCarouselSliderControl({
    super.key,
    required this.parent,
    required this.control,
    required this.children,
    required this.backend,
  });

  @override
  State<FletCarouselSliderControl> createState() =>
      _FletCarouselSliderControlState();
}

class _FletCarouselSliderControlState
    extends State<FletCarouselSliderControl> {
  final CarouselSliderController _controller = CarouselSliderController();
  final ScrollController _dotScrollController = ScrollController(); // add this


  int _current = 0;
  // ── Lifecycle ─────────────────────────────────────────────────────────────

  @override
  void didUpdateWidget(covariant FletCarouselSliderControl oldWidget) {
    super.didUpdateWidget(oldWidget);
    _handleAnimateToCommand();
  }

  // ── Command handler (Python → Dart) ───────────────────────────────────────
  // Supports:
  //   "index:durationMs:curveId"   → animateToPage
  //   "__next:durationMs:curveId"  → nextPage
  //   "__prev:durationMs:curveId"  → previousPage
  //   "__jump:index:none"          → jumpToPage (no animation)

  // ── Command handler (Python → Dart) ───────────────────────────────────────
  // Format: "action:param1:param2:counter"
  // The counter (last segment) is a monotonically increasing int from Python
  // that makes every call produce a unique string — so the same command can
  // be called multiple times in a row without being ignored.
  //
  // We track the last executed cmd string and skip if unchanged (guards
  // against didUpdateWidget firing for unrelated prop changes mid-animation).

  String? _lastCmd;

  void _handleAnimateToCommand() {
    final cmd = widget.control.attrString("__animateTo");
    if (cmd == null || cmd.isEmpty || cmd == _lastCmd) return;
    _lastCmd = cmd;

    // parts: [action, param1, param2, counter]
    final parts   = cmd.split(':');
    final action  = parts[0];
    final durMs   = parts.length > 1 ? (int.tryParse(parts[1]) ?? 300) : 300;
    final curveId = parts.length > 2 ? parts[2] : "fastOutSlowIn";

    switch (action) {
      case "__next":
        _controller.nextPage(
          duration: Duration(milliseconds: durMs),
          curve: _parseCurve(curveId),
        );
        break;
      case "__prev":
        _controller.previousPage(
          duration: Duration(milliseconds: durMs),
          curve: _parseCurve(curveId),
        );
        break;
      case "__jump":
        final index = int.tryParse(parts.length > 1 ? parts[1] : "0") ?? 0;
        _controller.jumpToPage(index);
        break;
      default:
        // animate_to_page — action is the page index string
        final index = int.tryParse(action) ?? 0;
        _controller.animateToPage(
          index,
          duration: Duration(milliseconds: durMs),
          curve: _parseCurve(curveId),
        );
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  Curve _parseCurve(String id) {
    switch (id) {
      case "linear":         return Curves.linear;
      case "easeIn":         return Curves.easeIn;
      case "easeOut":        return Curves.easeOut;
      case "easeInOut":      return Curves.easeInOut;
      case "bounceIn":       return Curves.bounceIn;
      case "bounceOut":      return Curves.bounceOut;
      case "elasticIn":      return Curves.elasticIn;
      case "elasticOut":     return Curves.elasticOut;
      case "decelerate":     return Curves.decelerate;
      case "fastOutSlowIn":  return Curves.fastOutSlowIn;
      default:               return Curves.fastOutSlowIn;
    }
  }

  Axis _parseAxis(String? value) =>
      value == "vertical" ? Axis.vertical : Axis.horizontal;

  Clip _parseClip(String? value) {
    switch (value) {
      case "none":                   return Clip.none;
      case "hardEdge":               return Clip.hardEdge;
      case "antiAlias":              return Clip.antiAlias;
      case "antiAliasWithSaveLayer": return Clip.antiAliasWithSaveLayer;
      default:                       return Clip.hardEdge;
    }
  }

  CenterPageEnlargeStrategy _parseEnlargeStrategy(String? value) {
    switch (value) {
      case "height": return CenterPageEnlargeStrategy.height;
      case "zoom":   return CenterPageEnlargeStrategy.zoom;
      default:       return CenterPageEnlargeStrategy.scale;
    }
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    // ── CarouselOptions params ───────────────────────────────────────
    final height                      = widget.control.attrDouble("height");
    final aspectRatio                 = widget.control.attrDouble("aspectRatio", 16 / 9)!;
    final viewportFraction            = widget.control.attrDouble("viewportFraction", 0.8)!;
    final initialPage                 = widget.control.attrInt("initialPage", 0)!;
    final enableInfiniteScroll        = widget.control.attrBool("enableInfiniteScroll", true)!;
    final animateToClosest            = widget.control.attrBool("animateToClosest", true)!;
    final reverse                     = widget.control.attrBool("reverse", false)!;
    final autoPlay                    = widget.control.attrBool("autoPlay", false)!;
    final autoPlayIntervalMs          = widget.control.attrInt("autoPlayInterval", 4000)!;
    final autoPlayAnimationDurationMs = widget.control.attrInt("autoPlayAnimationDuration", 800)!;
    final autoPlayCurveStr            = widget.control.attrString("autoPlayCurve");
    final enlargeCenterPage           = widget.control.attrBool("enlargeCenterPage", false)!;
    final enlargeStrategyStr          = widget.control.attrString("enlargeStrategy");
    final enlargeFactor               = widget.control.attrDouble("enlargeFactor", 0.3)!;
    final pageSnapping                = widget.control.attrBool("pageSnapping", true)!;
    final scrollDirectionStr          = widget.control.attrString("scrollDirection");
    final pauseAutoPlayOnTouch        = widget.control.attrBool("pauseAutoPlayOnTouch", true)!;
    final pauseAutoPlayOnManualNav    = widget.control.attrBool("pauseAutoPlayOnManualNavigate", true)!;
    final pauseAutoPlayInFiniteScroll = widget.control.attrBool("pauseAutoPlayInFiniteScroll", false)!;
    final disableCenter               = widget.control.attrBool("disableCenter", false)!;
    final padEnds                     = widget.control.attrBool("padEnds", true)!;
    final disablegesture              = widget.control.attrBool("disableGesture", false)!;
    final clipBehaviorStr             = widget.control.attrString("clipBehavior");
    final buildOnDemand               = widget.control.attrBool("build_on_demand", false)!;
    final enable_indicator            = widget.control.attrBool("enableindicator", true)!;
    final indicatorRowWidth           = widget.control.attrDouble("indicatorwidth");
    final indicatorActiveColor        = widget.control.attrColor("indicatorActiveColor", context);
    
    final indicatorInactiveColor      = widget.control.attrColor("indicatorInactiveColor", context);
    // ── Build children ───────────────────────────────────────────────
    // final List<Widget> items = widget.children.map((child) {
    //   return createControl(widget.control, child.id, widget.control.isDisabled);
    // }).toList();

    CarouselOptions _buildOptions(){
      return CarouselOptions(
        height:                        height,
        aspectRatio:                   aspectRatio,
        viewportFraction:              viewportFraction,
        initialPage:                   initialPage,
        enableInfiniteScroll:          enableInfiniteScroll,
        animateToClosest:              animateToClosest,
        reverse:                       reverse,
        autoPlay:                      autoPlay,
        autoPlayInterval:              Duration(milliseconds: autoPlayIntervalMs),
        autoPlayAnimationDuration:     Duration(milliseconds: autoPlayAnimationDurationMs),
        autoPlayCurve:                 _parseCurve(autoPlayCurveStr ?? "fastOutSlowIn"),
        enlargeCenterPage:             enlargeCenterPage,
        enlargeStrategy:               _parseEnlargeStrategy(enlargeStrategyStr),
        enlargeFactor:                 enlargeFactor,
        // scrollPhysics:                 PageScrollPhysics.,
        pageSnapping:                  pageSnapping,
        scrollDirection:               _parseAxis(scrollDirectionStr),
        pauseAutoPlayOnTouch:          pauseAutoPlayOnTouch,
        pauseAutoPlayOnManualNavigate: pauseAutoPlayOnManualNav,
        pauseAutoPlayInFiniteScroll:   pauseAutoPlayInFiniteScroll,
        disableCenter:                 disableCenter,
        padEnds:                       padEnds,
        clipBehavior:                  _parseClip(clipBehaviorStr),
        onPageChanged: (index, reason) {
          setState(() => _current = index); // <-- was just _current = index
          const dotWidth = 20.0;
          _dotScrollController.animateTo(
            (index * dotWidth) - 80,
            duration: Duration(milliseconds: 300),
            curve: Curves.easeInOut,
          );
          widget.backend.triggerControlEvent(
            widget.control.id, "change", "$index:${reason.name}",
          );
        },
        onScrolled: (value) {
          widget.backend.triggerControlEvent(
            widget.control.id,
            "scrolled",
            (value ?? 0.0).toStringAsFixed(4),
          );
        },
      );
    }


    final children = widget.children;
    if (buildOnDemand) {
      // final itemCount                   = widget.control.attrInt("itemcount", )!;
      if(enable_indicator){
        return Column(children: [
          Expanded(
            child: CarouselSlider.builder(
            controller: _controller,
            itemCount: children.length,
            disableGesture: disablegesture,
            itemBuilder: (context, index, realIndex) {
              final child = children[index];

              return createControl(
                widget.control,
                child.id,
                widget.control.isDisabled,
              );
            },
            options: _buildOptions(),
          ),
          ),
          SizedBox(
            width: indicatorRowWidth,
            child: ShaderMask(
              shaderCallback: (Rect bounds) {
                return LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  colors: [Colors.transparent, Colors.white, Colors.white, Colors.transparent],
                  stops: [0.0, 0.1, 0.9, 1.0],
                ).createShader(bounds);
              },
              blendMode: BlendMode.dstIn,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                controller: _dotScrollController,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: children.asMap().entries.map((entry) {
                    return GestureDetector(
                      onTap: () => _controller.animateToPage(entry.key),
                      child: Container(
                        width: 12.0,
                        height: 12.0,
                        margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: (_current == entry.key
                            ? (indicatorActiveColor ?? 
                              (Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black))
                            : (indicatorInactiveColor ?? 
                              (Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black))
                          ).withValues(alpha: _current == entry.key ? 0.9 : 0.4),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ))
        ]);
      }else {
        return CarouselSlider.builder(
          controller: _controller,
          itemCount: children.length,
          disableGesture: disablegesture,
          itemBuilder: (context, index, realIndex) {
            final child = children[index];

            return createControl(
              widget.control,
              child.id,
              widget.control.isDisabled,
            );
          },
          options: _buildOptions(),
        );
      }
    } else {
      // Only build all widgets if NOT lazy
      final items = children.map((child) {
        return createControl(
          widget.control,
          child.id,
          widget.control.isDisabled,
        );
      }).toList();

      if (enable_indicator){
        return Column(children: [
          Expanded(
            child: CarouselSlider(
            controller: _controller,
            items: items,
            disableGesture: disablegesture,
            options: _buildOptions(),
          ),
          ),
          SizedBox(
            width: indicatorRowWidth,
            child:  ShaderMask(
              shaderCallback: (Rect bounds) {
                return LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  colors: [
                    Colors.transparent,
                    Colors.white,
                    Colors.white,
                    Colors.transparent,
                  ],
                  stops: [0.0, 0.1, 0.9, 1.0],
                ).createShader(bounds);
              },
              blendMode: BlendMode.dstIn,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                controller: _dotScrollController,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: items.asMap().entries.map((entry) {
                    return GestureDetector(
                      onTap: () => _controller.animateToPage(entry.key),
                      child: Container(
                        width: 12.0,
                        height: 12.0,
                        margin: EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: (_current == entry.key
                            ? (indicatorActiveColor ?? 
                              (Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black))
                            : (indicatorInactiveColor ?? 
                              (Theme.of(context).brightness == Brightness.dark ? Colors.white : Colors.black))
                          ).withValues(alpha: _current == entry.key ? 0.9 : 0.4),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),)
        ]);
      }
      else {return CarouselSlider(
        controller: _controller,
        items: items,
        disableGesture: disablegesture,
        options: _buildOptions(),
      );}
}
  }
  @override
  void dispose() {
    _dotScrollController.dispose();
    super.dispose();
  }
}

