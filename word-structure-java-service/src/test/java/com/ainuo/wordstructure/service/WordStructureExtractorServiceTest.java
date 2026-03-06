package com.ainuo.wordstructure.service;

import com.ainuo.wordstructure.domain.model.StructureNode;
import com.ainuo.wordstructure.util.HeadingLevelDetector;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.io.ByteArrayOutputStream;
import java.util.List;

public class WordStructureExtractorServiceTest {
    @Test
    void shouldBuildTreeByHeadingLevel() throws Exception {
        RuleEngineService ruleEngineService = Mockito.mock(RuleEngineService.class);
        Mockito.when(ruleEngineService.classify(Mockito.anyString()))
                .thenReturn(new RuleClassifyResult("container", 0.5, "default"));
        WordStructureExtractorService service = new WordStructureExtractorService(new HeadingLevelDetector(), ruleEngineService);
        byte[] doc = buildDoc();
        ExtractionPayload result = service.extract(doc, "demo.docx");
        Assertions.assertEquals(2, result.getStructure().size());
        StructureNode first = result.getStructure().get(0);
        Assertions.assertEquals("1 总体情况", first.getTitle());
        Assertions.assertEquals(1, first.getChildren().size());
        Assertions.assertEquals("1.1 细分结构", first.getChildren().get(0).getTitle());
    }

    private byte[] buildDoc() throws Exception {
        try (XWPFDocument document = new XWPFDocument(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            XWPFParagraph p1 = document.createParagraph();
            p1.setStyle("Heading1");
            p1.createRun().setText("1 总体情况");

            XWPFParagraph p2 = document.createParagraph();
            p2.setStyle("Heading2");
            p2.createRun().setText("1.1 细分结构");

            XWPFParagraph p3 = document.createParagraph();
            p3.setStyle("Heading1");
            p3.createRun().setText("2 结论");
            document.write(out);
            return out.toByteArray();
        }
    }
}
