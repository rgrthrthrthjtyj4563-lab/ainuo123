package com.ainuo.wordstructure.util;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class HeadingLevelDetectorTest {
    private final HeadingLevelDetector detector = new HeadingLevelDetector();

    @Test
    void shouldDetectNumericHeading() {
        Assertions.assertEquals(1, detector.detectByText("1 总体情况"));
        Assertions.assertEquals(2, detector.detectByText("1.1 区域分布"));
        Assertions.assertEquals(3, detector.detectByText("1.1.1 结论"));
    }

    @Test
    void shouldDetectChineseHeading() {
        Assertions.assertEquals(1, detector.detectByText("一、背景"));
        Assertions.assertEquals(2, detector.detectByText("（一）样本分布"));
    }

    @Test
    void shouldIgnoreLongSentence() {
        Assertions.assertNull(detector.detectByText("这是一个非常长的描述性句子，主要用于说明现状，不应被识别成章节标题。"));
    }
}
