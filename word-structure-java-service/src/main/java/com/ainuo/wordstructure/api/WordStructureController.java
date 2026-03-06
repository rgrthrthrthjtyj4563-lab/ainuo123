package com.ainuo.wordstructure.api;

import com.ainuo.wordstructure.application.WordStructureApplicationService;
import com.ainuo.wordstructure.domain.model.ExtractionResult;
import org.springframework.http.MediaType;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/v1/structures")
public class WordStructureController {
    private final WordStructureApplicationService wordStructureApplicationService;

    public WordStructureController(WordStructureApplicationService wordStructureApplicationService) {
        this.wordStructureApplicationService = wordStructureApplicationService;
    }

    @PostMapping(value = "/extract", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public DataResponse<ExtractionResponse> extract(@RequestPart("file") MultipartFile file) throws Exception {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("文件不能为空");
        }
        String name = file.getOriginalFilename();
        if (!StringUtils.hasText(name) || !name.toLowerCase().endsWith(".docx")) {
            throw new IllegalArgumentException("仅支持Word文件 (.docx)");
        }
        ExtractionResult result = wordStructureApplicationService.extract(file.getBytes(), name);
        ExtractionResponse response = new ExtractionResponse();
        response.setExtractionId(result.getExtractionId());
        response.setStructure(result.getStructure());
        return DataResponse.ok(response);
    }
}
