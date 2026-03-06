package com.ainuo.wordstructure.domain.model;

import java.util.List;

public class ExtractionResult {
    private String fileName;
    private String fileHash;
    private List<StructureNode> structure;
    private Long extractionId;

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }

    public String getFileHash() {
        return fileHash;
    }

    public void setFileHash(String fileHash) {
        this.fileHash = fileHash;
    }

    public List<StructureNode> getStructure() {
        return structure;
    }

    public void setStructure(List<StructureNode> structure) {
        this.structure = structure;
    }

    public Long getExtractionId() {
        return extractionId;
    }

    public void setExtractionId(Long extractionId) {
        this.extractionId = extractionId;
    }
}
