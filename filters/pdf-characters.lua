-- PDF only: print characters that the PDF's Ubuntu font lacks (menu arrows
-- in "Layer ▸ Add Layer", and the minute and second marks in 35°54′36″)
-- from Latin Modern Math (\pdfsymbolfont, set in assets/pdf-unicode.tex).
-- This is done here rather than with newunicodechar, because unicode-math
-- makes ′ and ″ math characters, which then fail in running text.
if not FORMAT:match("latex") then
  return {}
end

local subs = {
  ["▸"] = "\\raisebox{0.12ex}{\\scalebox{0.7}{\\ensuremath{\\blacktriangleright}}}",
  ["′"] = "{\\pdfsymbolfont\\symbol{8242}}",
  ["″"] = "{\\pdfsymbolfont\\symbol{8243}}",
  ["ⁿ"] = "\\textsuperscript{n}",
}

local function split(text)
  local out, buf = {}, ""
  for _, cp in utf8.codes(text) do
    local ch = utf8.char(cp)
    if subs[ch] then
      if buf ~= "" then table.insert(out, pandoc.Str(buf)); buf = "" end
      table.insert(out, pandoc.RawInline("latex", subs[ch]))
    else
      buf = buf .. ch
    end
  end
  if buf ~= "" then table.insert(out, pandoc.Str(buf)) end
  return out
end

return {
  Str = function(el)
    for ch in pairs(subs) do
      if el.text:find(ch, 1, true) then return split(el.text) end
    end
  end,
}
