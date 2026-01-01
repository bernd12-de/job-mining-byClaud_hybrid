package de.layher.jobmining.kotlinapi.infrastructure.bridge

class PythonBridge {
    fun callSpacyExtractor(text: String): List<String> {
        val process = ProcessBuilder("python3", "scripts/spacy_extractor.py", text)
            .redirectError(ProcessBuilder.Redirect.INHERIT)
            .start()

        return process.inputStream.bufferedReader().readLines()
    }
}
