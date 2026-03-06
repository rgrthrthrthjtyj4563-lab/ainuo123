package com.ainuo.wordstructure.benchmark;

import com.ainuo.wordstructure.service.RuleClassifyResult;
import com.ainuo.wordstructure.service.RuleEngineService;
import com.ainuo.wordstructure.service.WordStructureExtractorService;
import com.ainuo.wordstructure.util.HeadingLevelDetector;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;
import org.mockito.Mockito;

import java.io.ByteArrayOutputStream;

@State(Scope.Benchmark)
public class WordStructureJmhBenchmark {
    private WordStructureExtractorService service;
    private byte[] doc;

    @Setup
    public void setup() throws Exception {
        RuleEngineService ruleEngineService = Mockito.mock(RuleEngineService.class);
        Mockito.when(ruleEngineService.classify(Mockito.anyString())).thenReturn(new RuleClassifyResult("container", 0.5, "k"));
        service = new WordStructureExtractorService(new HeadingLevelDetector(), ruleEngineService);
        try (XWPFDocument document = new XWPFDocument(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            for (int i = 1; i <= 500; i++) {
                XWPFParagraph p = document.createParagraph();
                p.setStyle(i % 2 == 0 ? "Heading2" : "Heading1");
                p.createRun().setText(i + " 标题");
            }
            document.write(out);
            doc = out.toByteArray();
        }
    }

    @Benchmark
    public Object extractBenchmark() {
        return service.extract(doc, "bench.docx");
    }
}
