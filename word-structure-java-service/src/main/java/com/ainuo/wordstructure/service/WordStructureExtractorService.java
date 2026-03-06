package com.ainuo.wordstructure.service;

import com.ainuo.wordstructure.domain.model.StructureNode;
import com.ainuo.wordstructure.util.HashUtil;
import com.ainuo.wordstructure.util.HeadingLevelDetector;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFParagraph;
import org.springframework.stereotype.Service;

import java.io.ByteArrayInputStream;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class WordStructureExtractorService {
    private final HeadingLevelDetector headingLevelDetector;
    private final RuleEngineService ruleEngineService;

    public WordStructureExtractorService(HeadingLevelDetector headingLevelDetector, RuleEngineService ruleEngineService) {
        this.headingLevelDetector = headingLevelDetector;
        this.ruleEngineService = ruleEngineService;
    }

    public ExtractionPayload extract(byte[] fileContent, String fileName) {
        String fileHash = HashUtil.sha256(fileContent);
        List<StructureNode> roots = new ArrayList<>();
        Deque<LevelNode> stack = new ArrayDeque<>();
        AtomicLong tempId = new AtomicLong(0);
        try (XWPFDocument document = new XWPFDocument(new ByteArrayInputStream(fileContent))) {
            for (XWPFParagraph paragraph : document.getParagraphs()) {
                String text = paragraph.getText();
                if (text == null || text.trim().isEmpty()) {
                    continue;
                }
                Integer level = headingLevelDetector.detectLevel(paragraph);
                if (level == null) {
                    continue;
                }
                StructureNode node = buildNode(text.trim(), level, tempId.incrementAndGet());
                while (!stack.isEmpty() && stack.peek().level >= level) {
                    stack.pop();
                }
                if (stack.isEmpty()) {
                    roots.add(node);
                } else {
                    stack.peek().node.getChildren().add(node);
                }
                stack.push(new LevelNode(level, node));
            }
        } catch (Exception e) {
            throw new IllegalArgumentException("无法解析Word文件: " + e.getMessage(), e);
        }
        ExtractionPayload payload = new ExtractionPayload();
        payload.setFileName(fileName);
        payload.setFileHash(fileHash);
        payload.setStructure(roots);
        return payload;
    }

    private StructureNode buildNode(String title, Integer level, Long tempId) {
        RuleClassifyResult classify = ruleEngineService.classify(title);
        StructureNode node = new StructureNode();
        node.setTempId(tempId);
        node.setTitle(title);
        node.setLevel(level);
        node.setNodeType(classify.getNodeType());
        node.setConfidenceScore(classify.getConfidence());
        node.setAiReasoning(classify.getReason());
        node.setAiGenerated(Boolean.TRUE);
        node.setShowDataTable("data_analysis".equals(classify.getNodeType()));
        node.setShowAiInterpretation(Boolean.FALSE);
        return node;
    }

    private static class LevelNode {
        private final Integer level;
        private final StructureNode node;

        private LevelNode(Integer level, StructureNode node) {
            this.level = level;
            this.node = node;
        }
    }
}
