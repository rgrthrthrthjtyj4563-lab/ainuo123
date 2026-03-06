package com.ainuo.wordstructure.util;

import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.springframework.stereotype.Component;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Component
public class HeadingLevelDetector {
    private static final Pattern HEADING_PATTERN = Pattern.compile("Heading\\s*(\\d)", Pattern.CASE_INSENSITIVE);
    private static final Pattern CN_HEADING_PATTERN = Pattern.compile("标题\\s*(\\d)");
    private static final Pattern NUMERIC_PATTERN = Pattern.compile("^(\\d+(?:\\.\\d+){0,5})(?:[.、\\s]|$)");
    private static final Pattern START_NUMBER_PATTERN = Pattern.compile("^\\d+\\s+");
    private static final Pattern CN_CHAPTER_PATTERN = Pattern.compile("^[一二三四五六七八九十]+、");
    private static final Pattern CN_SUB_PATTERN = Pattern.compile("^（[一二三四五六七八九十]+）");
    private static final Pattern PAREN_SUB_PATTERN = Pattern.compile("^[（(]\\d+[)）]");

    public Integer detectLevel(XWPFParagraph paragraph) {
        if (paragraph == null) {
            return null;
        }
        String styleName = "";
        if (paragraph.getStyle() != null) {
            styleName = paragraph.getStyle();
        }
        Integer fromStyle = detectByStyle(styleName);
        if (fromStyle != null) {
            return fromStyle;
        }
        String text = paragraph.getText() == null ? "" : paragraph.getText().trim();
        return detectByText(text);
    }

    Integer detectByStyle(String styleName) {
        if (styleName == null || styleName.isBlank()) {
            return null;
        }
        Matcher matcher = HEADING_PATTERN.matcher(styleName);
        if (matcher.find()) {
            int level = Integer.parseInt(matcher.group(1));
            if (level >= 1 && level <= 3) {
                return level;
            }
        }
        Matcher cn = CN_HEADING_PATTERN.matcher(styleName);
        if (cn.find()) {
            int level = Integer.parseInt(cn.group(1));
            if (level >= 1 && level <= 3) {
                return level;
            }
        }
        return null;
    }

    Integer detectByText(String text) {
        if (text == null || text.isBlank() || text.length() > 120) {
            return null;
        }
        if (text.matches(".*[。！？.!?]$")) {
            return null;
        }
        Matcher numeric = NUMERIC_PATTERN.matcher(text);
        if (numeric.find()) {
            int level = Math.min(numeric.group(1).split("\\.").length, 3);
            if (level == 1 && (text.length() > 40 || text.contains("：") || text.contains(":") || text.contains("；") || text.contains(";"))) {
                return null;
            }
            return level;
        }
        if (START_NUMBER_PATTERN.matcher(text).find()) {
            if (text.length() > 40 || text.contains("：") || text.contains(":") || text.contains("；") || text.contains(";")) {
                return null;
            }
            return 1;
        }
        if (CN_CHAPTER_PATTERN.matcher(text).find()) {
            if (text.length() > 40 || text.contains("：") || text.contains(":") || text.contains("；") || text.contains(";")) {
                return null;
            }
            return 1;
        }
        if (CN_SUB_PATTERN.matcher(text).find() || PAREN_SUB_PATTERN.matcher(text).find()) {
            return 2;
        }
        return null;
    }
}
