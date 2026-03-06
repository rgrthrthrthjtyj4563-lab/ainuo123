package com.ainuo.wordstructure.domain.model;

import java.util.ArrayList;
import java.util.List;

public class StructureNode {
    private Long tempId;
    private String title;
    private Integer level;
    private String nodeType;
    private Double confidenceScore;
    private String aiReasoning;
    private Boolean aiGenerated;
    private Boolean showDataTable;
    private Boolean showAiInterpretation;
    private List<StructureNode> children = new ArrayList<>();

    public Long getTempId() {
        return tempId;
    }

    public void setTempId(Long tempId) {
        this.tempId = tempId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public Integer getLevel() {
        return level;
    }

    public void setLevel(Integer level) {
        this.level = level;
    }

    public String getNodeType() {
        return nodeType;
    }

    public void setNodeType(String nodeType) {
        this.nodeType = nodeType;
    }

    public Double getConfidenceScore() {
        return confidenceScore;
    }

    public void setConfidenceScore(Double confidenceScore) {
        this.confidenceScore = confidenceScore;
    }

    public String getAiReasoning() {
        return aiReasoning;
    }

    public void setAiReasoning(String aiReasoning) {
        this.aiReasoning = aiReasoning;
    }

    public Boolean getAiGenerated() {
        return aiGenerated;
    }

    public void setAiGenerated(Boolean aiGenerated) {
        this.aiGenerated = aiGenerated;
    }

    public Boolean getShowDataTable() {
        return showDataTable;
    }

    public void setShowDataTable(Boolean showDataTable) {
        this.showDataTable = showDataTable;
    }

    public Boolean getShowAiInterpretation() {
        return showAiInterpretation;
    }

    public void setShowAiInterpretation(Boolean showAiInterpretation) {
        this.showAiInterpretation = showAiInterpretation;
    }

    public List<StructureNode> getChildren() {
        return children;
    }

    public void setChildren(List<StructureNode> children) {
        this.children = children;
    }
}
