import { Breadcrumb } from "../../../components/breadcrumb";
import { CreateObjectForm } from "../../../features/create/create-object-form";

export default function NewKnowledgePage() {
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/knowledge", label: "知识" },
          { label: "新建" },
        ]}
      />
      <CreateObjectForm operation="CreateKnowledge" heading="创建知识" extra="domain" />
    </article>
  );
}
