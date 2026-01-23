import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# Create a message with the PowerPoint Skill
response = client.beta.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]
    },
    messages=[
        {
            "role": "user",
            "content": "Create a presentation about LLMs and agentswith 5 slides",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)

print("Initial response:")
print(response.content)
print("\n" + "=" * 70)

# Extract file ID from response - it's in the tool_result content
file_id = None

# Check if we need to handle tool use
if response.stop_reason == "tool_use":
    print("\n🔧 Tool use detected, checking for file ID in tool results...")

    # Look through all content blocks
    for block in response.content:
        print(f"\nBlock type: {block.type}")

        if block.type == "tool_use":
            print(f"  Tool name: {block.name}")
            print(f"  Tool input: {block.input}")

            # Check if there's output with a file
            if hasattr(block, "output"):
                print(f"  Tool output: {block.output}")

                # Check for file in output
                if isinstance(block.output, dict) and "files" in block.output:
                    files = block.output.get("files", [])
                    if files and len(files) > 0:
                        file_id = files[0].get("id")
                        print(f"  Found file ID in output: {file_id}")

        elif block.type == "tool_result":
            print(f"  Tool result content: {block.content}")

            # Check for file_id in tool result content
            if isinstance(block.content, list):
                for item in block.content:
                    if hasattr(item, "file_id"):
                        file_id = item.file_id
                        print(f"  Found file ID in tool result: {file_id}")
                        break
                    elif isinstance(item, dict) and "file_id" in item:
                        file_id = item["file_id"]
                        print(f"  Found file ID in tool result dict: {file_id}")
                        break

# Also check the usage object for file information
if hasattr(response, "usage") and hasattr(response.usage, "output_files"):
    print(f"\nOutput files in usage: {response.usage.output_files}")
    if response.usage.output_files:
        # File ID might be here
        for file_info in response.usage.output_files:
            if hasattr(file_info, "id"):
                file_id = file_info.id
                print(f"Found file ID in usage.output_files: {file_id}")
                break

if file_id:
    print(f"\n📄 File ID found: {file_id}")
    print("📥 Downloading file...")

    # Download the file
    file_content = client.beta.files.download(
        file_id=file_id, betas=["files-api-2025-04-14"]
    )

    # Save to disk
    output_filename = "renewable_energy.pptx"
    with open(output_filename, "wb") as f:
        file_content.write_to_file(f.name)

    print(f"✅ Presentation saved to {output_filename}")
else:
    print("\n⚠️ No file ID found in response")
    print("\nFull response object attributes:")
    print(dir(response))
