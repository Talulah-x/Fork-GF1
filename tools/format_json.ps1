# 格式化JSON文件，保持数组在一行
# 作用于assets\resource\pipeline\tasks目录下的所有JSON文件

# 引入System.Web.Extensions以使用JavaScriptSerializer
Add-Type -AssemblyName System.Web.Extensions

# 创建JavaScriptSerializer实例
$serializer = New-Object System.Web.Extensions.JavaScriptSerializer
# 增加最大JSON长度限制，因为有些文件可能很大
$serializer.MaxJsonLength = 67108864

# 自定义格式化函数，保持数组在一行
function Format-JsonWithArraysInline {
    param (
        [Parameter(Mandatory = $true)]
        [string]$JsonString
    )

    # 首先解析JSON
    $jsonObject = $serializer.DeserializeObject($JsonString)
    
    # 然后使用ConvertTo-Json，但我们需要处理其输出
    $formattedJson = ConvertTo-Json -InputObject $jsonObject -Depth 100
    
    # 使用正则表达式替换数组格式，使其保持在一行
    # 匹配形如 "array": [\n    item1,\n    item2\n] 的模式
    $formattedJson = $formattedJson -replace '(\[)(?:\s*\r?\n\s*)([^[\]\r\n]*?)(?:\s*\r?\n\s*)(\])', '$1$2$3'
    
    # 处理嵌套数组，如 [item1, [subitem1, subitem2], item3]
    $formattedJson = $formattedJson -replace '(\[)(?:\s*\r?\n\s*)([^[\]\r\n]*?)(?:\s*\r?\n\s*)(\[)(?:\s*\r?\n\s*)([^[\]\r\n]*?)(?:\s*\r?\n\s*)(\])(?:\s*\r?\n\s*)([^[\]\r\n]*?)(?:\s*\r?\n\s*)(\])', '$1$2$3$4$5$6$7'
    
    return $formattedJson
}

# 获取所有JSON文件
$jsonFiles = Get-ChildItem -Path "c:\Users\25547\Desktop\MaaGF1_Test\assets\resource\pipeline\tasks" -Filter "*.json" -Recurse

# 处理每个文件
foreach ($file in $jsonFiles) {
    Write-Host "正在处理: $($file.FullName)"
    
    try {
        # 读取文件内容
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
        
        # 格式化内容
        $formattedContent = Format-JsonWithArraysInline -JsonString $content
        
        # 写回文件
        $formattedContent | Out-File -FilePath $file.FullName -Encoding UTF8
        
        Write-Host "已完成: $($file.FullName)" -ForegroundColor Green
    }
    catch {
        Write-Host "处理文件时出错: $($file.FullName)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host "所有JSON文件格式化完成！" -ForegroundColor Cyan