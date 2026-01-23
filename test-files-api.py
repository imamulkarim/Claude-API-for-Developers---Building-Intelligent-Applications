import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic()

print("=" * 70)
print("📁 Files API - List and Download Demo")
print("=" * 70)

# STEP 1: List all files
print("\n🔹 STEP 1: Listing all files in your workspace")
print("-" * 70)

try:
    files_list = client.beta.files.list(betas=["files-api-2025-04-14"])

    print(f"\n📋 Found {len(files_list.data)} file(s):\n")

    downloadable_files = []

    for i, file in enumerate(files_list.data, 1):
        print(f"{i}. File ID: {file.id}")
        print(f"   Filename: {file.filename}")
        print(f"   MIME Type: {file.mime_type}")
        print(f"   Size: {file.size_bytes / 1024:.2f} KB")
        print(f"   Created: {file.created_at}")
        print(f"   Downloadable: {file.downloadable}")

        # Track downloadable files (created by code execution tool)
        if file.downloadable:
            downloadable_files.append(file)

        print("-" * 70)

    if not files_list.data:
        print("   No files found. Run test-skills.py first to create a file!")

    # STEP 2: Download files that are downloadable
    if downloadable_files:
        print(
            f"\n🔹 STEP 2: Downloading {len(downloadable_files)} downloadable file(s)"
        )
        print("-" * 70)

        for file in downloadable_files:
            print(f"\n📥 Downloading: {file.filename}")
            print(f"   File ID: {file.id}")

            # Download the file content
            file_content = client.beta.files.download(
                file_id=file.id, betas=["files-api-2025-04-14"]
            )

            # Create downloads directory if it doesn't exist
            os.makedirs("downloads", exist_ok=True)

            # Save the file
            output_path = f"downloads/{file.filename}"
            with open(output_path, "wb") as f:
                file_content.write_to_file(f.name)

            print(f"   ✅ Saved to: {output_path}")
            print(f"   Size: {os.path.getsize(output_path) / 1024:.2f} KB")

    elif files_list.data:
        print("\n🔹 STEP 2: Download Status")
        print("-" * 70)
        print("\n⚠️  No downloadable files found.")
        print(
            "   Note: You can only download files created by the code execution tool."
        )
        print("   Files you uploaded cannot be downloaded.")

    # STEP 3: Get metadata for a specific file (if any exist)
    if files_list.data:
        print("\n🔹 STEP 3: Getting detailed metadata for first file")
        print("-" * 70)

        first_file = files_list.data[0]
        metadata = client.beta.files.retrieve_metadata(
            file_id=first_file.id, betas=["files-api-2025-04-14"]
        )

        print(f"\n📄 File Metadata:")
        print(f"   ID: {metadata.id}")
        print(f"   Type: {metadata.type}")
        print(f"   Filename: {metadata.filename}")
        print(f"   MIME Type: {metadata.mime_type}")
        print(f"   Size: {metadata.size_bytes / 1024:.2f} KB")
        print(f"   Created At: {metadata.created_at}")
        print(f"   Downloadable: {metadata.downloadable}")

    # Summary
    print("\n" + "=" * 70)
    print("✅ FILES API DEMO COMPLETE")
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"   • Total files: {len(files_list.data)}")
    print(f"   • Downloadable files: {len(downloadable_files)}")
    if downloadable_files:
        print(f"   • Downloaded to: ./downloads/")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"   Type: {type(e).__name__}")
