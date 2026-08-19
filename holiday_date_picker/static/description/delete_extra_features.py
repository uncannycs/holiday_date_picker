import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: Match from <!-- Feature Card 9 --> up to the last </div> before <!-- SCREENSHOTS TAB -->
# To be safe, let's match <!-- Feature Card 9 --> up to the end of Feature Card 17's div.
# Feature Card 17 ends with:
#                                     </div>
#                                 </div>
#                             </div>
#                         </div>

# A simpler approach: string replacement since we have the exact file contents.
# Let's find the start of Feature Card 9 and the end of Feature Card 17.
start_str = "<!-- Feature Card 9 -->"
end_str = "<!-- SCREENSHOTS TAB -->"

start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    # We want to keep the closing divs for the grid and tab pane
    # The string just before end_idx has closing divs. Let's find the position of the </div> that closes Feature Card 17.
    # Feature card 17 looks like this at the end:
    #                                             <p class="text-muted mb-0" style="font-size: 14px; line-height: 1.6">
    #                                                 Depends on stock and stock_account so valuation-aware inventory analysis
    #                                                 stays consistent.
    #                                             </p>
    #                                         </div>
    #                                     </div>
    #                                 </div>
    #                             </div>
    
    # Let's just use regex to remove <!-- Feature Card 9 --> up to the </div> that precedes `                            </div>\n                        </div>\n                    </div>\n                </div>\n                <!-- SCREENSHOTS TAB -->`
    
    pattern = r"(\s*<!-- Feature Card 9 -->.*?)(                            </div>\n                        </div>\n                    </div>\n                </div>\n                <!-- SCREENSHOTS TAB -->)"
    
    new_content = re.sub(pattern, r"\2", content, flags=re.DOTALL)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
        print("Success")
else:
    print("Could not find markers")
