#!/usr/bin/env python
import sys

if sys.version_info[0] == 3:
    unichr = chr

from PyQt4 import QtCore, QtGui

fontAwesomeFontId = -1

#The font-awesome icon painter
class QtAwesomeCharIconPainter(object):
    def paint(self, awesome, painter, rect, mode, state, options):
        painter.save()

        #set the correct color
        color = options.get("color")
        text = options.get("text")

        if mode == QtGui.QIcon.Disabled:
            color = options.get("color-disabled")
            alt = options.get("text-disabled") 
            if alt:
                text = "%s" % alt
        elif mode == QtGui.QIcon.Active:
            color = options.get("color-active")
            alt = options.get("text-active")
            if alt:
                text = "%s" % alt
        elif mode == QtGui.QIcon.Selected:
            color = options.get("color-selected")
            alt = options.get("text-selected")
            if alt:
                text = "%s" % alt
            
        painter.setPen(color)

        # add some 'padding' around the icon
        drawSize = QtCore.qRound(rect.height() * options.get("scale-factor"))
        painter.setFont(awesome.font(drawSize))
        painter.drawText(rect, QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter, text)
        painter.restore()

#The painter icon engine.
class QtAwesomeIconPainterIconEngine(QtGui.QIconEngine):
    def __init__(self, awesome, painter, options):
        super(QtAwesomeIconPainterIconEngine, self).__init__()
        self.awesome = awesome
        self.painter = painter
        self.options = options
    
    def clone(self):
        return QtAwesomeIconPainterIconEngine(self.awesome, self.painter, self.options)
    
    def paint(self, painter, rect, mode, state):
        self.painter.paint( self.awesome, painter, rect, mode, state, self.options )

    def pixmap(self, size, mode, state):
        pm = QtGui.QPixmap(size)
        pm.fill( QtCore.Qt.transparent )
        painter = QtGui.QPainter()
        painter.begin(pm)
        self.paint(painter, QtCore.QRect(QtCore.QPoint(0,0),size), mode, state)
        return pm

#The main class for managing icons
#This class requires a 2-phase construction. You must first create the class and then initialize it via an init* method
class QtAwesome(QtCore.QObject):
    def __init__(self, parent = None):
        super(QtAwesome, self).__init__(parent)
        
        # initialize the default options
        self.default_options = {
            "color": QtGui.QColor(50,50,50),
            "color-disabled": QtGui.QColor(70,70,70,60),
            "color-active": QtGui.QColor(10,10,10),
            "color-selected": QtGui.QColor(10,10,10),
            "scale-factor": 0.9,
            "text": None, 
            "text-disabled": None,
            "text-active": None,
            "text-selected": None
        }
        
        self._painter_map = {}

        self._font_icon_painter = QtAwesomeCharIconPainter()
    
    def setDefaultOption(self, name, value):
        self.default_options[name] = value
    
    def defaultOption(self, name):
        return self.default_options[name]

    def initFontAwesome(self, ttf_path):
        global fontAwesomeFontId
        
        if fontAwesomeFontId < 0:
            font_file = QtCore.QFile(ttf_path)
            if not font_file.open(QtCore.QIODevice.ReadOnly):
                print("Font awesome font could not be loaded!")
                return False
            
            font_data = font_file.readAll()
            font_file.close()
            fontAwesomeFontId = QtGui.QFontDatabase.addApplicationFontFromData(font_data)
        
        loadedFontFamilies = QtGui.QFontDatabase.applicationFontFamilies(fontAwesomeFontId)
        if loadedFontFamilies:
            self._font_name = loadedFontFamilies[0]
        else:
            print("Font awesome font is empty?!")
            fontAwesomeFontId = -1
            return False
        return True

    # Creates an icon with the given name
    # You can use the icon names as defined on http://fortawesome.github.io/Font-Awesome/design.html withour the 'icon-' prefix
    def icon(self, name, **options):
        options.update(self.default_options)
        if name in FONTAWESOMECODES:
            options["text"] = FONTAWESOMECODES[name]
            return self._icon( self._font_icon_painter, **options)
    
        if len(name) == 1:
            options["text"] = name
            return self._icon( self._font_icon_painter, **options)

        #this method first tries to retrieve the icon
        painter = self._painter_map.get(name)
        if not painter:
            return QtGui.QIcon()

        return self._icon(painter, **options)

    #Create a dynamic icon by simlpy supplying a painter object
    #The ownership of the painter is NOT transfered.
    def _icon(self, painter, **options):
        #Warning, when you use memoryleak detection. You should turn it of for the next call
        #QIcon's placed in gui items are often cached and not deleted when my memory-leak detection checks for leaks.
        # I'm not sure if it's a Qt bug or something I do wrong
        engine = QtAwesomeIconPainterIconEngine(self, painter, options)
        return QtGui.QIcon(engine)
    
    # Adds a named icon-painter to the QtAwesome icon map
    # As the name applies the ownership is passed over to QtAwesome
    #
    # @param name the name of the icon
    # @param painter the icon painter to add for this name
    def give(self, name, painter):
        if name in self._painter_map:
            p = self._painter_map.pop(name) # delete the old one
            p.deleteLater()
        self._painter_map[name] = painter

    #Creates/Gets the icon font with a given size in pixels. This can be usefull to use a label for displaying icons
    #Example:
    #
    #QLabel* label = new QLabel( QChar( icon_group ) );
    #label.setFont( awesome.font(16) )
    def font(self, size):
        font = QtGui.QFont(self._font_name)
        font.setPixelSize(size)
        return font

#A list of all icon-names with the codepoint (unicode-value) on the right
#You can use the names on the page http://fortawesome.github.io/Font-Awesome/design.html
_codepoints = [
    ("fa-adjust", 0xf042),
    ("fa-adn", 0xf170),
    ("fa-align-center", 0xf037),
    ("fa-align-justify", 0xf039),
    ("fa-align-left", 0xf036),
    ("fa-align-right", 0xf038),
    ("fa-ambulance", 0xf0f9),
    ("fa-anchor", 0xf13d),
    ("fa-android", 0xf17b),
    ("fa-angle-double-down", 0xf103),
    ("fa-angle-double-left", 0xf100),
    ("fa-angle-double-right", 0xf101),
    ("fa-angle-double-up", 0xf102),
    ("fa-angle-down", 0xf107),
    ("fa-angle-left", 0xf104),
    ("fa-angle-right", 0xf105),
    ("fa-angle-up", 0xf106),
    ("fa-apple", 0xf179),
    ("fa-archive", 0xf187),
    ("fa-arrow-circle-down", 0xf0ab),
    ("fa-arrow-circle-left", 0xf0a8),
    ("fa-arrow-circle-o-down", 0xf01a),
    ("fa-arrow-circle-o-left", 0xf190),
    ("fa-arrow-circle-o-right", 0xf18e),
    ("fa-arrow-circle-o-up", 0xf01b),
    ("fa-arrow-circle-right", 0xf0a9),
    ("fa-arrow-circle-up", 0xf0aa),
    ("fa-arrow-down", 0xf063),
    ("fa-arrow-left", 0xf060),
    ("fa-arrow-right", 0xf061),
    ("fa-arrow-up", 0xf062),
    ("fa-arrows", 0xf047),
    ("fa-arrows-alt", 0xf0b2),
    ("fa-arrows-h", 0xf07e),
    ("fa-arrows-v", 0xf07d),
    ("fa-asterisk", 0xf069),
    ("fa-automobile", 0xf1b9),
    ("fa-backward", 0xf04a),
    ("fa-ban", 0xf05e),
    ("fa-bank", 0xf19c),
    ("fa-bar-chart-o", 0xf080),
    ("fa-barcode", 0xf02a),
    ("fa-bars", 0xf0c9),
    ("fa-beer", 0xf0fc),
    ("fa-behance", 0xf1b4),
    ("fa-behance-square", 0xf1b5),
    ("fa-bell", 0xf0f3),
    ("fa-bell-o", 0xf0a2),
    ("fa-bitbucket", 0xf171),
    ("fa-bitbucket-square", 0xf172),
    ("fa-bitcoin", 0xf15a),
    ("fa-bold", 0xf032),
    ("fa-bolt", 0xf0e7),
    ("fa-bomb", 0xf1e2),
    ("fa-book", 0xf02d),
    ("fa-bookmark", 0xf02e),
    ("fa-bookmark-o", 0xf097),
    ("fa-briefcase", 0xf0b1),
    ("fa-btc", 0xf15a),
    ("fa-bug", 0xf188),
    ("fa-building", 0xf1ad),
    ("fa-building-o", 0xf0f7),
    ("fa-bullhorn", 0xf0a1),
    ("fa-bullseye", 0xf140),
    ("fa-cab", 0xf1ba),
    ("fa-calendar", 0xf073),
    ("fa-calendar-o", 0xf133),
    ("fa-camera", 0xf030),
    ("fa-camera-retro", 0xf083),
    ("fa-car", 0xf1b9),
    ("fa-caret-down", 0xf0d7),
    ("fa-caret-left", 0xf0d9),
    ("fa-caret-right", 0xf0da),
    ("fa-caret-square-o-down", 0xf150),
    ("fa-caret-square-o-left", 0xf191),
    ("fa-caret-square-o-right", 0xf152),
    ("fa-caret-square-o-up", 0xf151),
    ("fa-caret-up", 0xf0d8),
    ("fa-certificate", 0xf0a3),
    ("fa-chain", 0xf0c1),
    ("fa-chain-broken", 0xf127),
    ("fa-check", 0xf00c),
    ("fa-check-circle", 0xf058),
    ("fa-check-circle-o", 0xf05d),
    ("fa-check-square", 0xf14a),
    ("fa-check-square-o", 0xf046),
    ("fa-chevron-circle-down", 0xf13a),
    ("fa-chevron-circle-left", 0xf137),
    ("fa-chevron-circle-right", 0xf138),
    ("fa-chevron-circle-up", 0xf139),
    ("fa-chevron-down", 0xf078),
    ("fa-chevron-left", 0xf053),
    ("fa-chevron-right", 0xf054),
    ("fa-chevron-up", 0xf077),
    ("fa-child", 0xf1ae),
    ("fa-circle", 0xf111),
    ("fa-circle-o", 0xf10c),
    ("fa-circle-o-notch", 0xf1ce),
    ("fa-circle-thin", 0xf1db),
    ("fa-clipboard", 0xf0ea),
    ("fa-clock-o", 0xf017),
    ("fa-cloud", 0xf0c2),
    ("fa-cloud-download", 0xf0ed),
    ("fa-cloud-upload", 0xf0ee),
    ("fa-cny", 0xf157),
    ("fa-code", 0xf121),
    ("fa-code-fork", 0xf126),
    ("fa-codepen", 0xf1cb),
    ("fa-coffee", 0xf0f4),
    ("fa-cog", 0xf013),
    ("fa-cogs", 0xf085),
    ("fa-columns", 0xf0db),
    ("fa-comment", 0xf075),
    ("fa-comment-o", 0xf0e5),
    ("fa-comments", 0xf086),
    ("fa-comments-o", 0xf0e6),
    ("fa-compass", 0xf14e),
    ("fa-compress", 0xf066),
    ("fa-copy", 0xf0c5),
    ("fa-credit-card", 0xf09d),
    ("fa-crop", 0xf125),
    ("fa-crosshairs", 0xf05b),
    ("fa-css3", 0xf13c),
    ("fa-cube", 0xf1b2),
    ("fa-cubes", 0xf1b3),
    ("fa-cut", 0xf0c4),
    ("fa-cutlery", 0xf0f5),
    ("fa-dashboard", 0xf0e4),
    ("fa-database", 0xf1c0),
    ("fa-dedent", 0xf03b),
    ("fa-delicious", 0xf1a5),
    ("fa-desktop", 0xf108),
    ("fa-deviantart", 0xf1bd),
    ("fa-digg", 0xf1a6),
    ("fa-dollar", 0xf155),
    ("fa-dot-circle-o", 0xf192),
    ("fa-download", 0xf019),
    ("fa-dribbble", 0xf17d),
    ("fa-dropbox", 0xf16b),
    ("fa-drupal", 0xf1a9),
    ("fa-edit", 0xf044),
    ("fa-eject", 0xf052),
    ("fa-ellipsis-h", 0xf141),
    ("fa-ellipsis-v", 0xf142),
    ("fa-empire", 0xf1d1),
    ("fa-envelope", 0xf0e0),
    ("fa-envelope-o", 0xf003),
    ("fa-envelope-square", 0xf199),
    ("fa-eraser", 0xf12d),
    ("fa-eur", 0xf153),
    ("fa-euro", 0xf153),
    ("fa-exchange", 0xf0ec),
    ("fa-exclamation", 0xf12a),
    ("fa-exclamation-circle", 0xf06a),
    ("fa-exclamation-triangle", 0xf071),
    ("fa-expand", 0xf065),
    ("fa-external-link", 0xf08e),
    ("fa-external-link-square", 0xf14c),
    ("fa-eye", 0xf06e),
    ("fa-eye-slash", 0xf070),
    ("fa-facebook", 0xf09a),
    ("fa-facebook-square", 0xf082),
    ("fa-fast-backward", 0xf049),
    ("fa-fast-forward", 0xf050),
    ("fa-fax", 0xf1ac),
    ("fa-female", 0xf182),
    ("fa-fighter-jet", 0xf0fb),
    ("fa-file", 0xf15b),
    ("fa-file-archive-o", 0xf1c6),
    ("fa-file-audio-o", 0xf1c7),
    ("fa-file-code-o", 0xf1c9),
    ("fa-file-excel-o", 0xf1c3),
    ("fa-file-image-o", 0xf1c5),
    ("fa-file-movie-o", 0xf1c8),
    ("fa-file-o", 0xf016),
    ("fa-file-pdf-o", 0xf1c1),
    ("fa-file-photo-o", 0xf1c5),
    ("fa-file-picture-o", 0xf1c5),
    ("fa-file-powerpoint-o", 0xf1c4),
    ("fa-file-sound-o", 0xf1c7),
    ("fa-file-text", 0xf15c),
    ("fa-file-text-o", 0xf0f6),
    ("fa-file-video-o", 0xf1c8),
    ("fa-file-word-o", 0xf1c2),
    ("fa-file-zip-o", 0xf1c6),
    ("fa-files-o", 0xf0c5),
    ("fa-film", 0xf008),
    ("fa-filter", 0xf0b0),
    ("fa-fire", 0xf06d),
    ("fa-fire-extinguisher", 0xf134),
    ("fa-flag", 0xf024),
    ("fa-flag-checkered", 0xf11e),
    ("fa-flag-o", 0xf11d),
    ("fa-flash", 0xf0e7),
    ("fa-flask", 0xf0c3),
    ("fa-flickr", 0xf16e),
    ("fa-floppy-o", 0xf0c7),
    ("fa-folder", 0xf07b),
    ("fa-folder-o", 0xf114),
    ("fa-folder-open", 0xf07c),
    ("fa-folder-open-o", 0xf115),
    ("fa-font", 0xf031),
    ("fa-forward", 0xf04e),
    ("fa-foursquare", 0xf180),
    ("fa-frown-o", 0xf119),
    ("fa-gamepad", 0xf11b),
    ("fa-gavel", 0xf0e3),
    ("fa-gbp", 0xf154),
    ("fa-ge", 0xf1d1),
    ("fa-gear", 0xf013),
    ("fa-gears", 0xf085),
    ("fa-gift", 0xf06b),
    ("fa-git", 0xf1d3),
    ("fa-git-square", 0xf1d2),
    ("fa-github", 0xf09b),
    ("fa-github-alt", 0xf113),
    ("fa-github-square", 0xf092),
    ("fa-gittip", 0xf184),
    ("fa-glass", 0xf000),
    ("fa-globe", 0xf0ac),
    ("fa-google", 0xf1a0),
    ("fa-google-plus", 0xf0d5),
    ("fa-google-plus-square", 0xf0d4),
    ("fa-graduation-cap", 0xf19d),
    ("fa-group", 0xf0c0),
    ("fa-h-square", 0xf0fd),
    ("fa-hacker-news", 0xf1d4),
    ("fa-hand-o-down", 0xf0a7),
    ("fa-hand-o-left", 0xf0a5),
    ("fa-hand-o-right", 0xf0a4),
    ("fa-hand-o-up", 0xf0a6),
    ("fa-hdd-o", 0xf0a0),
    ("fa-header", 0xf1dc),
    ("fa-headphones", 0xf025),
    ("fa-heart", 0xf004),
    ("fa-heart-o", 0xf08a),
    ("fa-history", 0xf1da),
    ("fa-home", 0xf015),
    ("fa-hospital-o", 0xf0f8),
    ("fa-html5", 0xf13b),
    ("fa-image", 0xf03e),
    ("fa-inbox", 0xf01c),
    ("fa-indent", 0xf03c),
    ("fa-info", 0xf129),
    ("fa-info-circle", 0xf05a),
    ("fa-inr", 0xf156),
    ("fa-instagram", 0xf16d),
    ("fa-institution", 0xf19c),
    ("fa-italic", 0xf033),
    ("fa-joomla", 0xf1aa),
    ("fa-jpy", 0xf157),
    ("fa-jsfiddle", 0xf1cc),
    ("fa-key", 0xf084),
    ("fa-keyboard-o", 0xf11c),
    ("fa-krw", 0xf159),
    ("fa-language", 0xf1ab),
    ("fa-laptop", 0xf109),
    ("fa-leaf", 0xf06c),
    ("fa-legal", 0xf0e3),
    ("fa-lemon-o", 0xf094),
    ("fa-level-down", 0xf149),
    ("fa-level-up", 0xf148),
    ("fa-life-bouy", 0xf1cd),
    ("fa-life-ring", 0xf1cd),
    ("fa-life-saver", 0xf1cd),
    ("fa-lightbulb-o", 0xf0eb),
    ("fa-link", 0xf0c1),
    ("fa-linkedin", 0xf0e1),
    ("fa-linkedin-square", 0xf08c),
    ("fa-linux", 0xf17c),
    ("fa-list", 0xf03a),
    ("fa-list-alt", 0xf022),
    ("fa-list-ol", 0xf0cb),
    ("fa-list-ul", 0xf0ca),
    ("fa-location-arrow", 0xf124),
    ("fa-lock", 0xf023),
    ("fa-long-arrow-down", 0xf175),
    ("fa-long-arrow-left", 0xf177),
    ("fa-long-arrow-right", 0xf178),
    ("fa-long-arrow-up", 0xf176),
    ("fa-magic", 0xf0d0),
    ("fa-magnet", 0xf076),
    ("fa-mail-forward", 0xf064),
    ("fa-mail-reply", 0xf112),
    ("fa-mail-reply-all", 0xf122),
    ("fa-male", 0xf183),
    ("fa-map-marker", 0xf041),
    ("fa-maxcdn", 0xf136),
    ("fa-medkit", 0xf0fa),
    ("fa-meh-o", 0xf11a),
    ("fa-microphone", 0xf130),
    ("fa-microphone-slash", 0xf131),
    ("fa-minus", 0xf068),
    ("fa-minus-circle", 0xf056),
    ("fa-minus-square", 0xf146),
    ("fa-minus-square-o", 0xf147),
    ("fa-mobile", 0xf10b),
    ("fa-mobile-phone", 0xf10b),
    ("fa-money", 0xf0d6),
    ("fa-moon-o", 0xf186),
    ("fa-mortar-board", 0xf19d),
    ("fa-music", 0xf001),
    ("fa-navicon", 0xf0c9),
    ("fa-openid", 0xf19b),
    ("fa-outdent", 0xf03b),
    ("fa-pagelines", 0xf18c),
    ("fa-paper-plane", 0xf1d8),
    ("fa-paper-plane-o", 0xf1d9),
    ("fa-paperclip", 0xf0c6),
    ("fa-paragraph", 0xf1dd),
    ("fa-paste", 0xf0ea),
    ("fa-pause", 0xf04c),
    ("fa-paw", 0xf1b0),
    ("fa-pencil", 0xf040),
    ("fa-pencil-square", 0xf14b),
    ("fa-pencil-square-o", 0xf044),
    ("fa-phone", 0xf095),
    ("fa-phone-square", 0xf098),
    ("fa-photo", 0xf03e),
    ("fa-picture-o", 0xf03e),
    ("fa-pied-piper", 0xf1a7),
    ("fa-pied-piper-alt", 0xf1a8),
    ("fa-pied-piper-square", 0xf1a7),
    ("fa-pinterest", 0xf0d2),
    ("fa-pinterest-square", 0xf0d3),
    ("fa-plane", 0xf072),
    ("fa-play", 0xf04b),
    ("fa-play-circle", 0xf144),
    ("fa-play-circle-o", 0xf01d),
    ("fa-plus", 0xf067),
    ("fa-plus-circle", 0xf055),
    ("fa-plus-square", 0xf0fe),
    ("fa-plus-square-o", 0xf196),
    ("fa-power-off", 0xf011),
    ("fa-print", 0xf02f),
    ("fa-puzzle-piece", 0xf12e),
    ("fa-qq", 0xf1d6),
    ("fa-qrcode", 0xf029),
    ("fa-question", 0xf128),
    ("fa-question-circle", 0xf059),
    ("fa-quote-left", 0xf10d),
    ("fa-quote-right", 0xf10e),
    ("fa-ra", 0xf1d0),
    ("fa-random", 0xf074),
    ("fa-rebel", 0xf1d0),
    ("fa-recycle", 0xf1b8),
    ("fa-reddit", 0xf1a1),
    ("fa-reddit-square", 0xf1a2),
    ("fa-refresh", 0xf021),
    ("fa-renren", 0xf18b),
    ("fa-reorder", 0xf0c9),
    ("fa-repeat", 0xf01e),
    ("fa-reply", 0xf112),
    ("fa-reply-all", 0xf122),
    ("fa-retweet", 0xf079),
    ("fa-rmb", 0xf157),
    ("fa-road", 0xf018),
    ("fa-rocket", 0xf135),
    ("fa-rotate-left", 0xf0e2),
    ("fa-rotate-right", 0xf01e),
    ("fa-rouble", 0xf158),
    ("fa-rss", 0xf09e),
    ("fa-rss-square", 0xf143),
    ("fa-rub", 0xf158),
    ("fa-ruble", 0xf158),
    ("fa-rupee", 0xf156),
    ("fa-save", 0xf0c7),
    ("fa-scissors", 0xf0c4),
    ("fa-search", 0xf002),
    ("fa-search-minus", 0xf010),
    ("fa-search-plus", 0xf00e),
    ("fa-send", 0xf1d8),
    ("fa-send-o", 0xf1d9),
    ("fa-share", 0xf064),
    ("fa-share-alt", 0xf1e0),
    ("fa-share-alt-square", 0xf1e1),
    ("fa-share-square", 0xf14d),
    ("fa-share-square-o", 0xf045),
    ("fa-shield", 0xf132),
    ("fa-shopping-cart", 0xf07a),
    ("fa-sign-in", 0xf090),
    ("fa-sign-out", 0xf08b),
    ("fa-signal", 0xf012),
    ("fa-sitemap", 0xf0e8),
    ("fa-skype", 0xf17e),
    ("fa-slack", 0xf198),
    ("fa-sliders", 0xf1de),
    ("fa-smile-o", 0xf118),
    ("fa-sort", 0xf0dc),
    ("fa-sort-alpha-asc", 0xf15d),
    ("fa-sort-alpha-desc", 0xf15e),
    ("fa-sort-amount-asc", 0xf160),
    ("fa-sort-amount-desc", 0xf161),
    ("fa-sort-asc", 0xf0de),
    ("fa-sort-desc", 0xf0dd),
    ("fa-sort-down", 0xf0dd),
    ("fa-sort-numeric-asc", 0xf162),
    ("fa-sort-numeric-desc", 0xf163),
    ("fa-sort-up", 0xf0de),
    ("fa-soundcloud", 0xf1be),
    ("fa-space-shuttle", 0xf197),
    ("fa-spinner", 0xf110),
    ("fa-spoon", 0xf1b1),
    ("fa-spotify", 0xf1bc),
    ("fa-square", 0xf0c8),
    ("fa-square-o", 0xf096),
    ("fa-stack-exchange", 0xf18d),
    ("fa-stack-overflow", 0xf16c),
    ("fa-star", 0xf005),
    ("fa-star-half", 0xf089),
    ("fa-star-half-empty", 0xf123),
    ("fa-star-half-full", 0xf123),
    ("fa-star-half-o", 0xf123),
    ("fa-star-o", 0xf006),
    ("fa-steam", 0xf1b6),
    ("fa-steam-square", 0xf1b7),
    ("fa-step-backward", 0xf048),
    ("fa-step-forward", 0xf051),
    ("fa-stethoscope", 0xf0f1),
    ("fa-stop", 0xf04d),
    ("fa-strikethrough", 0xf0cc),
    ("fa-stumbleupon", 0xf1a4),
    ("fa-stumbleupon-circle", 0xf1a3),
    ("fa-subscript", 0xf12c),
    ("fa-suitcase", 0xf0f2),
    ("fa-sun-o", 0xf185),
    ("fa-superscript", 0xf12b),
    ("fa-support", 0xf1cd),
    ("fa-table", 0xf0ce),
    ("fa-tablet", 0xf10a),
    ("fa-tachometer", 0xf0e4),
    ("fa-tag", 0xf02b),
    ("fa-tags", 0xf02c),
    ("fa-tasks", 0xf0ae),
    ("fa-taxi", 0xf1ba),
    ("fa-tencent-weibo", 0xf1d5),
    ("fa-terminal", 0xf120),
    ("fa-text-height", 0xf034),
    ("fa-text-width", 0xf035),
    ("fa-th", 0xf00a),
    ("fa-th-large", 0xf009),
    ("fa-th-list", 0xf00b),
    ("fa-thumb-tack", 0xf08d),
    ("fa-thumbs-down", 0xf165),
    ("fa-thumbs-o-down", 0xf088),
    ("fa-thumbs-o-up", 0xf087),
    ("fa-thumbs-up", 0xf164),
    ("fa-ticket", 0xf145),
    ("fa-times", 0xf00d),
    ("fa-times-circle", 0xf057),
    ("fa-times-circle-o", 0xf05c),
    ("fa-tint", 0xf043),
    ("fa-toggle-down", 0xf150),
    ("fa-toggle-left", 0xf191),
    ("fa-toggle-right", 0xf152),
    ("fa-toggle-up", 0xf151),
    ("fa-trash-o", 0xf014),
    ("fa-tree", 0xf1bb),
    ("fa-trello", 0xf181),
    ("fa-trophy", 0xf091),
    ("fa-truck", 0xf0d1),
    ("fa-try", 0xf195),
    ("fa-tumblr", 0xf173),
    ("fa-tumblr-square", 0xf174),
    ("fa-turkish-lira", 0xf195),
    ("fa-twitter", 0xf099),
    ("fa-twitter-square", 0xf081),
    ("fa-umbrella", 0xf0e9),
    ("fa-underline", 0xf0cd),
    ("fa-undo", 0xf0e2),
    ("fa-university", 0xf19c),
    ("fa-unlink", 0xf127),
    ("fa-unlock", 0xf09c),
    ("fa-unlock-alt", 0xf13e),
    ("fa-unsorted", 0xf0dc),
    ("fa-upload", 0xf093),
    ("fa-usd", 0xf155),
    ("fa-user", 0xf007),
    ("fa-user-md", 0xf0f0),
    ("fa-users", 0xf0c0),
    ("fa-video-camera", 0xf03d),
    ("fa-vimeo-square", 0xf194),
    ("fa-vine", 0xf1ca),
    ("fa-vk", 0xf189),
    ("fa-volume-down", 0xf027),
    ("fa-volume-off", 0xf026),
    ("fa-volume-up", 0xf028),
    ("fa-warning", 0xf071),
    ("fa-wechat", 0xf1d7),
    ("fa-weibo", 0xf18a),
    ("fa-weixin", 0xf1d7),
    ("fa-wheelchair", 0xf193),
    ("fa-windows", 0xf17a),
    ("fa-won", 0xf159),
    ("fa-wordpress", 0xf19a),
    ("fa-wrench", 0xf0ad),
    ("fa-xing", 0xf168),
    ("fa-xing-square", 0xf169),
    ("fa-yahoo", 0xf19e),
    ("fa-yen", 0xf157),
    ("fa-youtube", 0xf167),
    ("fa-youtube-play", 0xf16a),
    ("fa-youtube-square", 0xf166) ]
FONTAWESOMECODES = dict(( (code[0], unichr(code[1])) for code in _codepoints ))
