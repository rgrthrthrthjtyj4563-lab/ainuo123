package com.ainuo.wordstructure.service;

import com.ainuo.wordstructure.util.HeadingLevelDetector;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.io.ByteArrayOutputStream;

public class PerformanceBenchmarkTest {
    @Test
    void extractionShouldMeetBaseline() throws Exception {
        RuleEngineService ruleEngineService = Mockito.mock(RuleEngineService.class);
        Mockito.when(ruleEngineService.classify(Mockito.anyString()))
                .thenReturn(new RuleClassifyResult("data_analysis", 0.8, "k"));
        WordStructureExtractorService service = new WordStructureExtractorService(new HeadingLevelDetector(), ruleEngineService);
        byte[] doc = buildLargeDoc(300);
        long start = System.nanoTime();
        service.extract(doc, "perf.docx");
        long elapsedMs = (System.nanoTime() - start) / 1_000_000;
        Assertions.assertTrue(elapsedMs < 600, "算法执行超过基线阈值");
    }

    private byte[] buildLargeDoc(int count) throws Exception {
        try (XWPFDocument document = new XWPFDocument(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            for (int i = 1; i <= count; i++) {
                XWPFParagraph p = document.createParagraph();
                p.setStyle(i % 2 == 0 ? "Heading2" : "Heading1");
                p.createRun().setText(i + " 标题");
            }
            document.write(out);
            return out.toByteArray();
        }
    }
}
