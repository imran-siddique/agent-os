plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "1.9.21"
    id("org.jetbrains.intellij") version "1.16.1"
}

group = "com.agentos"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.google.code.gson:gson:2.10.1")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    testImplementation("junit:junit:4.13.2")
}

intellij {
    version.set("2023.3")
    type.set("IC") // IntelliJ IDEA Community Edition
    
    plugins.set(listOf(
        // No additional plugins required for basic functionality
    ))
}

tasks {
    // Set the JVM compatibility versions
    withType<JavaCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
    }
    withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions.jvmTarget = "17"
    }

    patchPluginXml {
        sinceBuild.set("231")
        untilBuild.set("243.*")
        
        pluginDescription.set("""
            <h1>Agent OS - AI Safety for Code</h1>
            <p>Kernel-level safety for AI coding assistants.</p>
            
            <h2>Features</h2>
            <ul>
                <li>🛡️ <b>Real-time policy enforcement</b> - Block destructive operations</li>
                <li>🔍 <b>Multi-model code review (CMVK)</b> - Verify with GPT-4, Claude, Gemini</li>
                <li>📋 <b>Complete audit trail</b> - Log every AI suggestion</li>
                <li>👥 <b>Team-shared policies</b> - Consistent safety across organization</li>
            </ul>
            
            <h2>What It Blocks</h2>
            <ul>
                <li>Destructive SQL (DROP, DELETE, TRUNCATE)</li>
                <li>Dangerous file operations (rm -rf)</li>
                <li>Hardcoded secrets and API keys</li>
                <li>Privilege escalation (sudo, chmod 777)</li>
            </ul>
        """.trimIndent())
        
        changeNotes.set("""
            <h2>0.1.0</h2>
            <ul>
                <li>Initial release</li>
                <li>Real-time code analysis with policy enforcement</li>
                <li>CMVK multi-model code review</li>
                <li>Audit logging</li>
                <li>Team policy sharing</li>
            </ul>
        """.trimIndent())
    }

    signPlugin {
        certificateChain.set(System.getenv("CERTIFICATE_CHAIN"))
        privateKey.set(System.getenv("PRIVATE_KEY"))
        password.set(System.getenv("PRIVATE_KEY_PASSWORD"))
    }

    publishPlugin {
        token.set(System.getenv("PUBLISH_TOKEN"))
    }
    
    buildSearchableOptions {
        enabled = false
    }
}
