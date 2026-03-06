package com.ainuo.wordstructure.api;

import com.ainuo.wordstructure.domain.model.StructureNode;

import java.util.List;

public class ExtractionResponse {
    private Long extractionId;
    private List<StructureNode> structure;

    public Long getExtractionId() {
        return extractionId;
    }

    public void setExtractionId(Long extractionId) {
        this.extractionId = extractionId;
    }

    public List<StructureNode> getStructure() {
        return structure;
    }

    public void setStructure(List<StructureNode> structure) {
        this.structure = structure;
    }
}
