import difflib
import html as _h


def _word_diff(original: str, compressed: str) -> tuple[str, str]:
    """
    Word-level SequenceMatcher diff.
    Returns (annotated_original_html, annotated_compressed_html).

    Colour key:
      original  — red strikethrough  = dropped
      original  — plain              = survived unchanged
      compressed — amber             = rewritten (replaced)
      compressed — green             = inserted (rare; model added a connector word)
      compressed — plain             = survived unchanged
    """
    orig_words = original.split()
    comp_words = compressed.split()
    matcher = difflib.SequenceMatcher(None, orig_words, comp_words, autojunk=False)

    orig_parts: list[str] = []
    comp_parts: list[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        ow = _h.escape(" ".join(orig_words[i1:i2]))
        cw = _h.escape(" ".join(comp_words[j1:j2]))

        if tag == "equal":
            orig_parts.append(ow)
            comp_parts.append(cw)

        elif tag == "delete":
            orig_parts.append(
                f'<mark style="background:#fee2e2;color:#b91c1c;'
                f'text-decoration:line-through;padding:1px 3px;border-radius:3px">{ow}</mark>'
            )

        elif tag == "insert":
            comp_parts.append(
                f'<mark style="background:#dcfce7;color:#15803d;'
                f'padding:1px 3px;border-radius:3px">{cw}</mark>'
            )

        elif tag == "replace":
            orig_parts.append(
                f'<mark style="background:#fee2e2;color:#b91c1c;'
                f'text-decoration:line-through;padding:1px 3px;border-radius:3px">{ow}</mark>'
            )
            comp_parts.append(
                f'<mark style="background:#fef9c3;color:#92400e;'
                f'padding:1px 3px;border-radius:3px">{cw}</mark>'
            )

    return " ".join(orig_parts), " ".join(comp_parts)


def render_diff_html(record: dict) -> str:
    """Build a self-contained side-by-side diff HTML block for a compression run."""
    original   = record.get("input_text", "")
    compressed = record.get("output_text", "")
    if not original or not compressed:
        return ""

    orig_html, comp_html = _word_diff(original, compressed)

    model      = _h.escape(record.get("model", "—"))
    tokenizer  = _h.escape(record.get("tokenizer", "—"))
    ts         = _h.escape(record.get("timestamp", "—"))
    in_tok     = record.get("input_tokens", "—")
    out_tok    = record.get("output_tokens", "—")
    target_tok = record.get("target_tokens", "—")
    ratio      = record.get("compression_ratio", 0)
    quality    = record.get("quality_score", 0)
    duration   = record.get("duration_ms", "—")
    run_id     = record.get("id", "—")

    feedback_val  = record.get("feedback")
    feedback_note = _h.escape(record.get("feedback_comment") or "")

    # Build optional feedback block
    if feedback_val is not None:
        badge_bg    = "#f0fdf4" if feedback_val == 1 else "#fef2f2"
        badge_color = "#15803d" if feedback_val == 1 else "#b91c1c"
        badge_text  = "👍 Helpful" if feedback_val == 1 else "👎 Not helpful"
        feedback_block = (
            f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:8px;'
            f'margin-top:10px;padding:8px 12px;border-radius:6px;background:{badge_bg}">'
            f'<span style="font-weight:600;font-size:0.8rem;color:{badge_color}">{badge_text}</span>'
        )
        if feedback_note:
            feedback_block += (
                f'<span style="font-size:0.8rem;color:#374151;font-style:italic">'
                f'"{feedback_note}"</span>'
            )
        feedback_block += "</div>"
    else:
        feedback_block = ""

    return f"""
<div style="font-family:system-ui,sans-serif;margin-top:4px">

  <!-- Primary meta chips -->
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px;font-size:0.78rem">
    <span style="background:#f3f4f6;padding:3px 9px;border-radius:12px;color:#374151">Run #{run_id}</span>
    <span style="background:#f3f4f6;padding:3px 9px;border-radius:12px;color:#374151">{ts}</span>
    <span style="background:#eff6ff;padding:3px 9px;border-radius:12px;color:#1d4ed8">{model}</span>
    <span style="background:#f0fdf4;padding:3px 9px;border-radius:12px;color:#15803d">Quality {quality:.4f}</span>
    <span style="background:#fff7ed;padding:3px 9px;border-radius:12px;color:#c2410c">Ratio {ratio:.4f}</span>
    <span style="background:#faf5ff;padding:3px 9px;border-radius:12px;color:#7e22ce">⏱ {duration} ms</span>
  </div>

  <!-- Secondary meta chips -->
  <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;font-size:0.78rem">
    <span style="background:#f3f4f6;padding:3px 9px;border-radius:12px;color:#374151">{in_tok} in → {out_tok} out (target {target_tok})</span>
    <span style="background:#f3f4f6;padding:3px 9px;border-radius:12px;color:#374151">tokenizer: {tokenizer}</span>
  </div>

  <!-- Side-by-side panels -->
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">

    <!-- Original -->
    <div style="border:1px solid #fecaca;border-radius:8px;overflow:hidden">
      <div style="background:#fef2f2;padding:8px 14px;border-bottom:1px solid #fecaca;
                  display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:700;font-size:0.8rem;color:#b91c1c;letter-spacing:.04em">ORIGINAL</span>
        <span style="font-size:0.75rem;color:#6b7280">{in_tok} tokens</span>
      </div>
      <div style="padding:14px;line-height:1.8;font-size:0.875rem;color:#1a1a1a;
                  max-height:340px;overflow-y:auto;word-break:break-word">
        {orig_html}
      </div>
    </div>

    <!-- Compressed -->
    <div style="border:1px solid #bbf7d0;border-radius:8px;overflow:hidden">
      <div style="background:#f0fdf4;padding:8px 14px;border-bottom:1px solid #bbf7d0;
                  display:flex;justify-content:space-between;align-items:center">
        <span style="font-weight:700;font-size:0.8rem;color:#15803d;letter-spacing:.04em">COMPRESSED</span>
        <span style="font-size:0.75rem;color:#6b7280">{out_tok} tokens</span>
      </div>
      <div style="padding:14px;line-height:1.8;font-size:0.875rem;color:#1a1a1a;
                  max-height:340px;overflow-y:auto;word-break:break-word">
        {comp_html}
      </div>
    </div>

  </div>

  {feedback_block}

  <!-- Legend -->
  <div style="display:flex;flex-wrap:wrap;gap:14px;margin-top:10px;font-size:0.75rem;color:#6b7280;align-items:center">
    <mark style="background:#fee2e2;color:#b91c1c;text-decoration:line-through;padding:2px 7px;border-radius:3px">dropped</mark>
    <mark style="background:#fef9c3;color:#92400e;padding:2px 7px;border-radius:3px">rewritten</mark>
    <mark style="background:#dcfce7;color:#15803d;padding:2px 7px;border-radius:3px">inserted</mark>
    <span>plain = unchanged</span>
  </div>

</div>
"""
